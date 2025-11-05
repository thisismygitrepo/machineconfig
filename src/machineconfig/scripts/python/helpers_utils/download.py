

import typer
from typing import Annotated, Optional



def download(
    url: Annotated[Optional[str], typer.Argument(..., help="The URL to download the file from.")] = None,
    decompress: Annotated[bool, typer.Option(..., "--decompress", "-d", help="Decompress the file if it's an archive.")] = False,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="The output file path.")] = None,
) -> None:

    if url is None:
        typer.echo("❌ Error: URL is required.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"📥 Downloading from: {url}")
    import requests
    import subprocess
    from requests import Response
    from pathlib import Path
    from urllib.parse import parse_qs, unquote, urlparse
    def _sanitize_candidate_filename(name: str) -> Optional[str]:
        candidate = Path(name).name.strip()
        if not candidate or candidate in {".", ".."}:
            return None
        return candidate
    def _filename_from_content_disposition(header_value: Optional[str]) -> Optional[str]:
        if header_value is None:
            return None
        parts = [segment.strip() for segment in header_value.split(";")]
        for part in parts:
            lower = part.lower()
            if lower.startswith("filename*="):
                value = part.split("=", 1)[1]
                value = value.strip().strip('"')
                if "''" in value:
                    value = value.split("''", 1)[1]
                decoded = unquote(value)
                sanitized = _sanitize_candidate_filename(decoded)
                if sanitized is not None:
                    return sanitized
            if lower.startswith("filename="):
                value = part.split("=", 1)[1].strip().strip('"')
                decoded = unquote(value)
                sanitized = _sanitize_candidate_filename(decoded)
                if sanitized is not None:
                    return sanitized
        return None
    def _filename_from_url(url: str) -> Optional[str]:
        parsed = urlparse(url)
        url_candidate = _sanitize_candidate_filename(unquote(Path(parsed.path).name))
        if url_candidate is not None:
            return url_candidate
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        for key, values in query_params.items():
            lower_key = key.lower()
            if "name" in lower_key or "file" in lower_key:
                for value in values:
                    sanitized = _sanitize_candidate_filename(unquote(value))
                    if sanitized is not None:
                        return sanitized
        return None
    def _resolve_download_path(url: str, response: Response, output: Optional[str]) -> Path:
        if output is not None:
            return Path(output)
        header_candidate = _filename_from_content_disposition(response.headers.get("content-disposition"))
        if header_candidate is not None:
            return Path(header_candidate)
        response_url_candidate = _filename_from_url(response.url)
        if response_url_candidate is not None:
            return Path(response_url_candidate)
        request_url_candidate = _filename_from_url(url)
        if request_url_candidate is not None:
            return Path(request_url_candidate)
        return Path("downloaded_file")


    try:
        response = requests.get(url, allow_redirects=True, stream=True, timeout=60)
        response.raise_for_status()
        download_path = _resolve_download_path(url=url, response=response, output=output)
        total_size = int(response.headers.get('content-length', 0))
        with open(download_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                chunk_size = 8192 * 4
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = (downloaded / total_size) * 100
                        typer.echo(f"\r⏬ Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", nl=False)
                typer.echo()
        typer.echo(f"✅ Downloaded to: {download_path}")
    except requests.exceptions.RequestException as e:
        typer.echo(f"❌ Download failed: {e}", err=True)
        raise typer.Exit(code=1)
    except OSError as e:
        typer.echo(f"❌ File write error: {e}", err=True)
        raise typer.Exit(code=1)
    
    if decompress:
        typer.echo(f"📦 Decompressing: {download_path}")
        
        base_name = download_path.name
        parts = base_name.split('.')
        base_name = parts[0] if parts else download_path.stem
        
        extract_dir = download_path.parent / base_name
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            subprocess.run(
                ["ouch", "decompress", str(download_path), "--dir", str(extract_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            typer.echo(f"✅ Decompressed to: {extract_dir}")
            
            if download_path.exists():
                download_path.unlink()
                typer.echo(f"🗑️  Removed archive: {download_path}")
                
        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ Decompression failed: {e.stderr}", err=True)
            raise typer.Exit(code=1)
        except FileNotFoundError:
            typer.echo("❌ Error: ouch command not found. Please install ouch.", err=True)
            typer.echo("💡 Install with: cargo install ouch", err=True)
            raise typer.Exit(code=1)
