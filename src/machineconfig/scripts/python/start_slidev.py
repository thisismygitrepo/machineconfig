
"""
slidev
"""

from machineconfig.utils.utils import CONFIG_PATH, PROGRAM_PATH
from crocodile.meta import Terminal, P
import subprocess
import platform


PORT_DEFAULT = 3030


root = CONFIG_PATH.joinpath(".cache/slidev")
if not root.joinpath("components").exists():
    # assert slidev is installed first
    Terminal(stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE).run(f"cd {root.parent};npm init slidev")


def main():
    import argparse
    parser = argparse.ArgumentParser()  
    parser.add_argument("-d", "--directory", default=None, help="Directory of the report")
    parser.add_argument("--port", default=PORT_DEFAULT, help=f"Port to serve the report, default to {PORT_DEFAULT}")
    args = parser.parse_args()

    port = args.port

    if args.directory is None:
        report_dir = P.cwd()
    else:
        report_dir = P(args.directory)
    assert report_dir.exists(), f"{report_dir} does not exist"
    assert report_dir.is_dir(), f"{report_dir} is not a directory"
    assert report_dir.joinpath("slides.md").exists(), f"slides.md not found in {report_dir}"
    report_dir.search().apply(lambda x: x.copy(folder=root, overwrite=True))

    from machineconfig.utils.utils import check_tool_exists
    check_tool_exists(tool_name="slidev", install_script="npm i -g @slidev/cli")

    print(f"Presentation is served at http://{platform.node()}:{port}")
    program: str = f"cd {root}; slidev --port {port} --remote 0.0.0.0"
    PROGRAM_PATH.write_text(program)


if __name__ == '__main__':
    main()
