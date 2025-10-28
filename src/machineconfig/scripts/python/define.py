
"""
Minimalist programs that only print scripts without frills so it can be sourced by by shell.
"""


import typer
import platform


def define_scripts():
    if platform.system() != "Linux":
        raise RuntimeError("This command is only supported on Linux systems.")
    from machineconfig.setup_linux import INTERACTIVE as script_path
    script = script_path.read_text(encoding="utf-8")
    print(script)


def main():
    app = typer.Typer(add_completion=False, no_args_is_help=True)
    app.command(name="scripts", help="define all scripts", no_args_is_help=False)(define_scripts)
    app()


# if __name__ == "__main__":
#     main()
