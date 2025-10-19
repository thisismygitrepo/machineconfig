

import typer
from typing import Annotated, Optional
from pathlib import Path
import subprocess
import requests


def download(
    url: Annotated[Optional[str], typer.Argument(..., help="The URL to download the file from.")] = None,
    decompress: Annotated[bool, typer.Option("--decompress", "-d", help="Decompress the file if it's an archive.")] = False,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="The output file path.")] = None,
) -> None:
    if url is None:
        typer.echo("❌ Error: URL is required.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"📥 Downloading from: {url}")    
    download_path = Path(output) if output else Path(url.split("/")[-1])
    
    try:
        response = requests.get(url, allow_redirects=True, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(download_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                chunk_size = 8192
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


def merge_pdfs(
        pdf1: Annotated[str, typer.Argument(..., help="Path to the first PDF file.")],
        pdf2: Annotated[str, typer.Argument(..., help="Path to the second PDF file.")],
        output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output merged PDF file path.")] = None,
        compress: Annotated[bool, typer.Option("--compress", "-c", help="Compress the output PDF.")] = False,
    ) -> None:
    def merge_pdfs_internal(pdf1: str, pdf2: str, output: Optional[str], compress: bool) -> None:
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        for pdf_path in [pdf1, pdf2]:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        output_path = output if output else "merged.pdf"
        if compress:
            try:
                for p in writer.pages:
                    try:
                        # PageObject.compress_content_streams exists in pypdf
                        p.compress_content_streams()
                    except Exception:
                        # best-effort: ignore per-page compression failures
                        continue
            except Exception:
                pass
            try:
                writer.compress_identical_objects()
            except Exception:
                # non-fatal if this fails
                pass
        writer.write(output_path)
        print(f"✅ Merged PDF saved to: {output_path}")
    from machineconfig.utils.meta import lambda_to_defstring
    code = lambda_to_defstring(lambda : merge_pdfs_internal(pdf1=pdf1, pdf2=pdf2, output=output, compress=compress), in_global=True)
    import tempfile
    tmp_py_file = Path(tempfile.mkstemp(suffix=".py")[1])
    tmp_py_file.write_text(code, encoding="utf-8")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(f"""uv run --with pypdf {tmp_py_file} """)


def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️ [u]  utilities operations", no_args_is_help=True, add_help_option=False, add_completion=False)
    app.command(name="download", no_args_is_help=True, help="[d] Download a file from a URL and optionally decompress it.")(download)
    app.command(name="d", no_args_is_help=True, hidden=True)(download)
    app.command(name="merge-pdfs", no_args_is_help=True, help="[m] Merge two PDF files into one.")(merge_pdfs)
    app.command(name="m", no_args_is_help=True, hidden=True)(merge_pdfs)
    return app
