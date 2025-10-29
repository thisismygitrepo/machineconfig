
import typer


def machineconfig_find():
    from machineconfig.scripts.python.helpers_msearch import FZFG_LINUX_PATH, FZFG_WINDOWS_PATH
    import platform
    if platform.system() == "Linux":
        script_path = FZFG_LINUX_PATH
    elif platform.system() == "Windows":
        script_path = FZFG_WINDOWS_PATH
    else:
        raise RuntimeError("Unsupported platform")
    import os
    op_program_path = os.getenv("OP_PROGRAM_PATH")
    if op_program_path is None:
        typer.echo("Error: OP_PROGRAM_PATH environment variable is not set, please run using `wrap_mcfg msearch` ", err=True)
        raise typer.Exit(code=1)
    from pathlib import Path
    op_program_path = Path(op_program_path)
    op_program_path.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8")
    # Use the script_path as needed
    # print(f"Using script at: {script_path}")


def main():
    app = typer.Typer(add_completion=False, no_args_is_help=True)
    app.command(name="msearch", help="machineconfig search helper", no_args_is_help=False)(machineconfig_find)
    app()
