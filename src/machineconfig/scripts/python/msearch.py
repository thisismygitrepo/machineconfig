
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
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=script_path.read_text(encoding="utf-8"), strict=False)


def main():
    app = typer.Typer(add_completion=False, no_args_is_help=True)
    app.command(name="msearch", help="machineconfig search helper", no_args_is_help=False)(machineconfig_find)
    app()
