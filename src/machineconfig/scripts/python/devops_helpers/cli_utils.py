

import typer
from typing import Annotated, Optional
from pathlib import Path
import subprocess
import requests

def download(url: Annotated[Optional[str], typer.Argument(..., help="The URL to download the file from." )] = None,
             decompress: Annotated[bool, typer.Option("--decompress", "-d", help="Decompress the file if it's an archive.")] = False,
             output: Annotated[Optional[str], typer.Option("--output", "-o", help="The output file path.")] = None) -> None:
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
        
        output_dir = download_path.parent if output else Path.cwd()
        
        try:
            _result = subprocess.run(
                ["ouch", "decompress", str(download_path), "--dir", str(output_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            typer.echo(f"✅ Decompressed to: {output_dir}")
            
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


def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️  [u]  utilities operations", no_args_is_help=True, add_completion=True)
    app.command(name="download", no_args_is_help=True, help="[d] Download a file from a URL and optionally decompress it.")(download)
    app.command(name="d", no_args_is_help=True, hidden=True)(download)
    return app
