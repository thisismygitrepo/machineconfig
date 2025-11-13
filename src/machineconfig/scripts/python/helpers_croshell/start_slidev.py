"""
slidev
"""

from machineconfig.utils.source_of_truth import CONFIG_ROOT
from machineconfig.utils.code import print_code
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.terminal import Response
from typing import Annotated, Optional
import typer
import subprocess
import platform

PORT_DEFAULT = 3030

SLIDEV_REPO = PathExtended(CONFIG_ROOT).joinpath(".cache/slidev")
if not SLIDEV_REPO.joinpath("components").exists():
    print("📦 Initializing Slidev repository...")
    subprocess.run(f"cd {SLIDEV_REPO.parent};npm init slidev@latest", check=False, shell=True, text=True)
    print("✅ Slidev repository initialized successfully!\n")


def _execute_with_shell(command: str) -> Response:
    if platform.system() == "Windows":
        completed = subprocess.run(["powershell", "-Command", command], capture_output=True, check=False, text=True)
    else:
        completed = subprocess.run(command, capture_output=True, check=False, text=True, shell=True)
    response = Response.from_completed_process(completed)
    response.print()
    return response


def jupyter_to_markdown(file: PathExtended):
    op_dir = file.parent.joinpath("presentation")
    print("📝 Converting Jupyter notebook to markdown...")

    # https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
    # from nbconvert.exporters.markdown import MarkdownExporter
    # import nbformat
    # nb = nbformat.read(file, as_version=4)
    # assert isinstance(nb, nbformat.notebooknode.NotebookNode), f"{file} is not a notebook"
    # e = MarkdownExporter(exclude_input=True, exclude_input_prompt=True, exclude_output_prompt=True)
    # body, resources = e.from_notebook_node(nb=nb)
    # op_dir.joinpath("slides_raw.md").write_text(body, encoding="utf-8")
    # for key, value in resources['outputs'].items():

    cmd = f"jupyter nbconvert --to markdown --no-prompt --no-input --output-dir {op_dir} --output slides_raw.md {file}"
    _execute_with_shell(cmd)
    cmd = f"jupyter nbconvert --to html --no-prompt --no-input --output-dir {op_dir} {file}"
    _execute_with_shell(cmd)

    op_file = op_dir.joinpath("slides_raw.md")
    slide_separator = "\n\n---\n\n"
    md = op_file.read_text(encoding="utf-8").replace("\n\n\n\n", slide_separator)
    md = slide_separator.join([item for item in md.split(slide_separator) if bool(item.strip())])
    op_file.with_name("slides.md").write_text(md, encoding="utf-8")
    print(f"✅ Conversion completed! Check the results at: {op_dir}\n")

    return op_dir


def main(
    directory: Annotated[Optional[str], typer.Option("-d", "--directory", help="📁 Directory of the report.")] = None,
    jupyter_file: Annotated[Optional[str], typer.Option("-j", "--jupyter-file", help="📓 Jupyter notebook file to convert to slides. If not provided, slides.md is used.")] = None,
) -> None:
    print("\n" + "=" * 50)
    print("🎥 Welcome to the Slidev Presentation Tool")
    print("=" * 50 + "\n")

    port = PORT_DEFAULT

    if jupyter_file is not None:
        print("📓 Jupyter file provided. Converting to markdown...")
        report_dir = jupyter_to_markdown(PathExtended(jupyter_file))
    else:
        if directory is None:
            report_dir = PathExtended.cwd()
        else:
            report_dir = PathExtended(directory)

    assert report_dir.exists(), f"❌ Directory {report_dir} does not exist."
    assert report_dir.is_dir(), f"❌ {report_dir} is not a directory."

    md_file = report_dir.joinpath("slides.md")
    if not md_file.exists():
        res = report_dir.search("*.md")
        if len(res) == 1:
            md_file = res[0]
        else:
            raise FileNotFoundError(f"❌ slides.md not found in {report_dir}")

    print("📂 Copying files to Slidev repository...")
    for item in report_dir.search():
        item.copy(folder=SLIDEV_REPO, overwrite=True)
    if md_file.name != "slides.md":
        SLIDEV_REPO.joinpath(md_file.name).with_name(name="slides.md", inplace=True, overwrite=True)

    import machineconfig.scripts.python.helpers_network.address as helper
    res = helper.select_lan_ipv4(prefer_vpn=False)
    if res is None:
        print("❌ Error: Could not determine local LAN IPv4 address for presentation.")
        raise typer.Exit(code=1)
    local_ip_v4 = res

    print("🌐 Presentation will be served at:")
    print(f"   - http://{platform.node()}:{port}")
    print(f"   - http://localhost:{port}")
    print(f"   - http://{local_ip_v4}:{port}\n")

    program = "npm run dev slides.md -- --remote"
    # PROGRAM_PATH.write_text(program, encoding="utf-8")
    import subprocess

    subprocess.run(program, shell=True, cwd=SLIDEV_REPO)
    print_code(code=program, lexer="bash", desc="Run the following command to start the presentation")


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
