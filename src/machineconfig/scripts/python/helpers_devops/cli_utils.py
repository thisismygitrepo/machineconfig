

import typer
from typing import Annotated, Literal, Optional, TypedDict
from pathlib import Path


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
    import requests
    import subprocess
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
    def merge_pdfs_internal(pdf1: str, pdf2: str, output: str | None, compress: bool) -> None:
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
    from machineconfig.utils.meta import lambda_to_python_script
    code = lambda_to_python_script(lambda : merge_pdfs_internal(pdf1=pdf1, pdf2=pdf2, output=output, compress=compress), in_global=True, import_module=False)
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_command, _py_file = get_uv_command_executing_python_script(python_script=code, uv_with=["pypdf"], uv_project_dir=None)
    run_shell_script(uv_command)


def compress_pdf(
        pdf_input: Annotated[str, typer.Argument(..., help="Path to the input PDF file to compress.")],
        output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output compressed PDF file path.")] = None,
        flate_level: Annotated[int, typer.Option("--flate-level", "-f", help="Flate compression level (0-9, default 9).")] = 9,
        recompress: Annotated[bool, typer.Option("--recompress", "-r", help="Recompress already compressed streams.")] = True,
        linearize: Annotated[bool, typer.Option("--linearize", "-l", help="Linearize PDF for faster web viewing.")] = False,
    ) -> None:
    def compress_pdf_internal(pdf_input: str, output: str | None, flate_level: int, recompress: bool, linearize: bool) -> None:
        from pikepdf import Pdf, ObjectStreamMode, settings
        settings.set_flate_compression_level(flate_level)
        output_path = output if output else pdf_input.replace(".pdf", "_compressed.pdf")
        with Pdf.open(pdf_input) as pdf:
            pdf.save(
                output_path,
                compress_streams=True,
                recompress_flate=recompress,
                object_stream_mode=ObjectStreamMode.generate,
                linearize=linearize,
            )
        print(f"✅ Compressed PDF saved to: {output_path}")
    from machineconfig.utils.meta import lambda_to_python_script
    code = lambda_to_python_script(
        lambda: compress_pdf_internal(pdf_input=pdf_input, output=output, flate_level=flate_level, recompress=recompress, linearize=linearize),
        in_global=True,
        import_module=False,
    )
    from machineconfig.utils.code import run_shell_script, get_uv_command_executing_python_script
    uv_command, _py_file = get_uv_command_executing_python_script(python_script=code, uv_with=["pikepdf"], uv_project_dir=None)
    run_shell_script(uv_command)


class MachineSpecs(TypedDict):
    system: str
    distro: str
    home_dir: str
def get_machine_specs() -> MachineSpecs:
    """Write print and return the local machine specs."""
    import platform
    UV_RUN_CMD = "$HOME/.local/bin/uv run" if platform.system() != "Windows" else """& "$env:USERPROFILE/.local/bin/uv" run"""
    command = f"""{UV_RUN_CMD} --with distro python -c "import distro; print(distro.name(pretty=True))" """
    import subprocess
    distro = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
    specs: MachineSpecs = {
        "system": platform.system(),
        "distro": distro,
        "home_dir": str(Path.home()),
    }
    print(specs)
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    path = CONFIG_ROOT.joinpath("machine_specs.json")
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    import json
    path.write_text(json.dumps(specs, indent=4), encoding="utf-8")
    return specs


def init_project(python: Annotated[Literal["3.13", "3.14"], typer.Option("--python", "-p", help="Python version for the uv virtual environment.")]= "3.13") -> None:
    _ = python
    repo_root = Path.cwd()
    if not (repo_root / "pyproject.toml").exists():
        typer.echo("❌ Error: pyproject.toml not found.", err=True)
        raise typer.Exit(code=1)
    print(f"Adding group `plot` with common data science and plotting packages...")
    script = """
uv add --group plot \
    # Data & computation
    numpy pandas polars duckdb-engine python-magic \
    # Plotting / visualization
    matplotlib plotly kaleido \
    # Notebooks / interactive
    ipython ipykernel jupyterlab nbformat marimo \
    # Code analysis / type checking / linting
    mypy pyright ruff pylint pyrefly \
    # Packaging / build / dev
    cleanpy \
    # CLI / debugging / utilities
    ipdb pudb \
    # Type hints for packages
    types-python-dateutil types-pyyaml types-requests types-tqdm \
    types-mysqlclient types-paramiko types-pytz types-sqlalchemy types-toml types-urllib3 \
"""
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script)
