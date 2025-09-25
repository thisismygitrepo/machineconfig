"""
slidev
"""

from machineconfig.utils.source_of_truth import CONFIG_PATH
from machineconfig.utils.code import print_code
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.terminal import Terminal
import subprocess
import platform

PORT_DEFAULT = 3030

SLIDEV_REPO = PathExtended(CONFIG_PATH).joinpath(".cache/slidev")
if not SLIDEV_REPO.joinpath("components").exists():
    print("📦 Initializing Slidev repository...")
    Terminal(stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE).run(f"cd {SLIDEV_REPO.parent};npm init slidev@latest")
    print("✅ Slidev repository initialized successfully!\n")


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
    Terminal().run(cmd, shell="powershell").print()
    cmd = f"jupyter nbconvert --to html --no-prompt --no-input --output-dir {op_dir} {file}"
    Terminal().run(cmd, shell="powershell").print()

    op_file = op_dir.joinpath("slides_raw.md")
    slide_separator = "\n\n---\n\n"
    md = op_file.read_text(encoding="utf-8").replace("\n\n\n\n", slide_separator)
    md = slide_separator.join([item for item in md.split(slide_separator) if bool(item.strip())])
    op_file.with_name("slides.md").write_text(md, encoding="utf-8")
    print(f"✅ Conversion completed! Check the results at: {op_dir}\n")

    return op_dir


def main() -> None:
    import argparse

    print("\n" + "=" * 50)
    print("🎥 Welcome to the Slidev Presentation Tool")
    print("=" * 50 + "\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", default=None, help="📁 Directory of the report.")
    parser.add_argument("-j", "--jupyter-file", default=None, help="📓 Jupyter notebook file to convert to slides. If not provided, slides.md is used.")
    args = parser.parse_args()

    port = PORT_DEFAULT

    if args.jupyter_file is not None:
        print("📓 Jupyter file provided. Converting to markdown...")
        report_dir = jupyter_to_markdown(PathExtended(args.jupyter_file))
    else:
        if args.directory is None:
            report_dir = PathExtended.cwd()
        else:
            report_dir = PathExtended(args.directory)

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

    import socket

    try:
        local_ip_v4 = socket.gethostbyname(socket.gethostname() + ".local")
    except Exception:
        print("⚠️ Warning: Could not get local_ip_v4. This might be due to running in a WSL instance.")
        local_ip_v4 = socket.gethostbyname(socket.gethostname())

    print("🌐 Presentation will be served at:")
    print(f"   - http://{platform.node()}:{port}")
    print(f"   - http://localhost:{port}")
    print(f"   - http://{local_ip_v4}:{port}\n")

    program = "npm run dev slides.md -- --remote"
    # PROGRAM_PATH.write_text(program, encoding="utf-8")
    import subprocess

    subprocess.run(program, shell=True, cwd=SLIDEV_REPO)
    print_code(code=program, lexer="bash", desc="Run the following command to start the presentation")


if __name__ == "__main__":
    main()
