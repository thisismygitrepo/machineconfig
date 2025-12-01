

from typing import Annotated, Optional
import typer
from pathlib import Path


def download(
    url: Annotated[Optional[str], typer.Argument(..., help="The URL to download the file from.")] = None,
    decompress: Annotated[bool, typer.Option(..., "--decompress", "-d", help="Decompress the file if it's an archive.")] = False,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="The output file path.")] = None,
    output_dir: Annotated[Optional[str], typer.Option("--output-dir", help="Directory to place the downloaded file in.")] = None,
) -> Optional["Path"]:
    import subprocess
    from urllib.parse import parse_qs, unquote, urlparse
    from requests import Response
    import requests
    from pathlib import Path
    if url is None:
        typer.echo("❌ Error: URL is required.", err=True)
        return None
    if output is not None and output_dir is not None:
        typer.echo("❌ Error: --output and --output-dir cannot be used together.", err=True)
        return None
    typer.echo(f"📥 Downloading from: {url}")

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

    def _filename_from_url(source_url: str) -> Optional[str]:
        parsed = urlparse(source_url)
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

    def _resolve_download_path(request_url: str, response: Response, requested_output: Optional[str], requested_output_dir: Optional[str]) -> Path:
        if requested_output is not None:
            return Path(requested_output)
        header_candidate = _filename_from_content_disposition(response.headers.get("content-disposition"))
        if header_candidate is None:
            header_candidate = _filename_from_url(response.url)
        if header_candidate is None:
            header_candidate = _filename_from_url(request_url)
        if header_candidate is None:
            header_candidate = "downloaded_file"
        if requested_output_dir is not None:
            return Path(requested_output_dir) / header_candidate
        return Path(header_candidate)

    try:
        with requests.get(url, allow_redirects=True, stream=True, timeout=60) as response:
            response.raise_for_status()
            download_path = _resolve_download_path(url, response, output, output_dir)
            download_path.parent.mkdir(parents=True, exist_ok=True)
            total_size_header = response.headers.get("content-length", "0")
            try:
                total_size = int(total_size_header)
            except (TypeError, ValueError):
                total_size = 0
            if total_size <= 0:
                with open(download_path, "wb") as file_handle:
                    file_handle.write(response.content)
            else:
                downloaded = 0
                chunk_size = 8192 * 40
                with open(download_path, "wb") as file_handle:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        file_handle.write(chunk)
                        downloaded += len(chunk)
                        progress = (downloaded / total_size) * 100
                        typer.echo(f"\r⏬ Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", nl=False)
                typer.echo()
    except requests.exceptions.RequestException as exception:
        typer.echo(f"❌ Download failed: {exception}", err=True)
        return None
    except OSError as exception:
        typer.echo(f"❌ File write error: {exception}", err=True)
        return None

    typer.echo(f"✅ Downloaded to: {download_path}")
    result_path: Path = download_path
    if decompress:
        typer.echo(f"📦 Decompressing: {download_path}")
        base_name = download_path.name.split(".", maxsplit=1)[0]  # ouch decompresses all (e.g. .tar.gz) in one go.
        if base_name in {"", ".", ".."}:
            base_name = "extracted"
        extract_dir = download_path.parent / base_name
        extract_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["ouch", "decompress", str(download_path), "--dir", str(extract_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            typer.echo(f"✅ Decompressed to: {extract_dir}")
            if download_path.exists():
                download_path.unlink()
                typer.echo(f"🗑️  Removed archive: {download_path}")
            result_path = extract_dir
        except subprocess.CalledProcessError as exception:
            typer.echo(f"❌ Decompression failed: {exception.stderr}", err=True)
            return None
        except FileNotFoundError:
            typer.echo("❌ Error: ouch command not found. Please install ouch.", err=True)
            typer.echo("💡 Install with: cargo install ouch", err=True)
            return None

    return result_path.resolve()


if __name__ == "__main__":
    pass
