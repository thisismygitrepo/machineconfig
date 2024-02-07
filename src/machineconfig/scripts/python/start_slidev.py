
"""
slidev
"""

from machineconfig.utils.utils import CONFIG_PATH, PROGRAM_PATH, print_code
from crocodile.meta import Terminal, P
# from crocodile.environment import get_network_addresses
import subprocess
import platform


PORT_DEFAULT = 3030


SLIDEV_REPO = CONFIG_PATH.joinpath(".cache/slidev")
if not SLIDEV_REPO.joinpath("components").exists():
    # assert slidev is installed first
    Terminal(stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE).run(f"cd {SLIDEV_REPO.parent};npm init slidev")


def jupyter_to_markdown(file: P):
    op_dir = file.parent.joinpath("presentation")

    # https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
    # from nbconvert.exporters.markdown import MarkdownExporter
    # import nbformat
    # nb = nbformat.read(file, as_version=4)
    # assert isinstance(nb, nbformat.notebooknode.NotebookNode), f"{file} is not a notebook"
    # e = MarkdownExporter(exclude_input=True, exclude_input_prompt=True, exclude_output_prompt=True)
    # body, resources = e.from_notebook_node(nb=nb)
    # op_dir.joinpath("slides_raw.md").write_text(body)
    # for key, value in resources['outputs'].items():

    cmd = f"jupyter nbconvert --to markdown --no-prompt --no-input --output-dir {op_dir} --output slides_raw.md {file}"
    Terminal().run(cmd, shell="powershell").print()
    cmd = f"jupyter nbconvert --to html --no-prompt --no-input --output-dir {op_dir} {file}"
    Terminal().run(cmd, shell="powershell").print()
    # cmd = f"jupyter nbconvert --to pdf --no-prompt --no-input --output-dir {op_dir} {file}"
    # Terminal().run(cmd, shell="powershell").print()


    op_file = op_dir.joinpath("slides_raw.md")
    slide_separator =  '\n\n---\n\n'
    md = op_file.read_text().replace('\n\n\n\n', slide_separator)
    md = slide_separator.join([item for item in md.split(slide_separator) if bool(item.strip())])  # remove empty slides.
    op_file.with_name("slides.md").write_text(md)
    return op_dir


def main() -> None:
    import argparse


    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", default=None, help="Directory of the report")
    parser.add_argument("-j", "--jupyter-file", default=None, help="Jupyter notebook file to convert to slides. If not provided, slides.md is used.")
    parser.add_argument("--port", default=PORT_DEFAULT, help=f"Port to serve the report, default to {PORT_DEFAULT}")
    args = parser.parse_args()

    port = args.port

    if args.jupyter_file is not None:
        report_dir = jupyter_to_markdown(P(args.jupyter_file))
    else:
        if args.directory is None:
            report_dir = P.cwd()
        else:
            report_dir = P(args.directory)

    assert report_dir.exists(), f"{report_dir} does not exist"
    assert report_dir.is_dir(), f"{report_dir} is not a directory"

    md_file = report_dir.joinpath("slides.md")
    if not md_file.exists():
        res = report_dir.search("*.md")
        if len(res) == 1:
            md_file = res.list[0]
        else:
            raise FileNotFoundError(f"slides.md not found in {report_dir}")

    report_dir.search().apply(lambda x: x.copy(folder=SLIDEV_REPO, overwrite=True))
    if md_file.name != "slides.md":
        SLIDEV_REPO.joinpath(md_file.name).with_name(name="slides.md", inplace=True, overwrite=True)

    # from machineconfig.utils.utils import check_tool_exists
    # check_tool_exists(tool_name="slidev", install_script="npm i -g @slidev/cli")

    import socket
    try: local_ip_v4 = socket.gethostbyname(socket.gethostname() + ".local")  # without .local, in linux machines, '/etc/hosts' file content, you have an IP address mapping with '127.0.1.1' to your hostname
    except Exception:
        print(f"Warning: Could not get local_ip_v4. This is probably because you are running a WSL instance")  # TODO find a way to get the local_ip_v4 in WSL
        local_ip_v4 = socket.gethostbyname(socket.gethostname())

    print(f"Presentation is served at http://{platform.node()}:{port}")
    print(f"Presentation is served at http://localhost:{port}")
    print(f"Presentation is served at http://{local_ip_v4}:{port}")
    program: str = f"cd {SLIDEV_REPO}; slidev --port {port} --remote 0.0.0.0; cd {P.cwd()}"
    PROGRAM_PATH.write_text(program)
    print_code(program, lexer="bash")


if __name__ == '__main__':
    main()
