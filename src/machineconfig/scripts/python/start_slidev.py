
"""
slidev
"""

from machineconfig.utils.utils import CONFIG_PATH, PROGRAM_PATH, print_code
from crocodile.meta import Terminal, P
import subprocess
import platform


PORT_DEFAULT = 3030


root = CONFIG_PATH.joinpath(".cache/slidev")
if not root.joinpath("components").exists():
    # assert slidev is installed first
    Terminal(stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE).run(f"cd {root.parent};npm init slidev")


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
    assert report_dir.joinpath("slides.md").exists(), f"slides.md not found in {report_dir}"
    report_dir.search().apply(lambda x: x.copy(folder=root, overwrite=True))

    # from machineconfig.utils.utils import check_tool_exists
    # check_tool_exists(tool_name="slidev", install_script="npm i -g @slidev/cli")

    print(f"Presentation is served at http://{platform.node()}:{port}")
    program: str = f"cd {root}; slidev --port {port} --remote 0.0.0.0"
    PROGRAM_PATH.write_text(program)
    print_code(program, lexer="bash")



if __name__ == '__main__':
    main()
