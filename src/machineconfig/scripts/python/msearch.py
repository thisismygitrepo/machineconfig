
import typer
from typing import Annotated


def machineconfig_search(
        directory: Annotated[str, typer.Option(..., "--directory", "-d", help="The directory to search")] = ".",
        ast: Annotated[bool, typer.Option(..., "--ast", "-a", help="The abstract syntax tree search/ tree sitter search of symbols")] = False):

    if ast:
        from machineconfig.scripts.python.helpers.ast_search import get_repo_symbols
        symbols = get_repo_symbols(directory)
        from machineconfig.utils.options import choose_from_options
        try:
            res = choose_from_options(options=symbols, msg="Select a symbol to search for:", fzf=True, multi=False)
            from rich import print_json
            import json
            res_json = json.dumps(res, indent=4)
            print_json(res_json)
            return None
        except Exception as e:
            print(f"❌ Error during selection: {e}")
            return None

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
    app.command(name="msearch", help="machineconfig search helper", no_args_is_help=False)(machineconfig_search)
    app()
