
import typer
from typing import Annotated


def machineconfig_search(
        directory: Annotated[str, typer.Option(..., "--directory", "-d", help="The directory to search")] = ".",
        ast: Annotated[bool, typer.Option(..., "--ast", "-a", help="The abstract syntax tree search/ tree sitter search of symbols")] = False,
        symantic: Annotated[bool, typer.Option(..., "--symantic", "-s", help="The symantic search of symbols")] = False,
        extension: Annotated[str, typer.Option(..., "--extension", "-e", help="File extension to filter by (e.g., .py, .js)")] = "",
        file: Annotated[bool, typer.Option(..., "--file", "-f", help="File search using fzf")] = False,
        no_dotfiles: Annotated[bool, typer.Option(..., "--no-dotfiles", "-D", help="Exclude dotfiles from search")] = False,
        rga: Annotated[bool, typer.Option(..., "--rga", "-a", help="Use ripgrep-all for searching instead of ripgrep")] = False,
        install_dependencies: Annotated[bool, typer.Option(..., "--install-dependencies", "-p", help="Install required dependencies if missing")] = False
        ):
    if install_dependencies:
        from machineconfig.utils.installer_utils.installer_cli import install_if_missing
        install_if_missing("fzf")
        install_if_missing("tv")
        install_if_missing("bat")
        install_if_missing("fd")
        install_if_missing("rg")  # ripgrep
        install_if_missing("rga")  # ripgrep-all
        # install_if_missing("tree-sitter-cli")
        return
    if symantic:
        script = ""
        for an_ex in extension.split(","):
            script = script + f"""\nparse *.{an_ex} """
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=script)
        return
    if ast:
        from machineconfig.scripts.python.helpers.ast_search import get_repo_symbols
        symbols = get_repo_symbols(directory)
        from machineconfig.utils.options import choose_from_options
        try:
            res = choose_from_options(options=symbols, msg="Select a symbol to search for:", tv=True, multi=False)
            from rich import print_json
            import json
            res_json = json.dumps(res, indent=4)
            print_json(res_json)
            return None
        except Exception as e:
            print(f"❌ Error during selection: {e}")
            return None
    if file:
        script = """fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}' """
        if no_dotfiles:
            script = "fd | " + script
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script=script)
        return
    from machineconfig.scripts.python.helpers_msearch import FZFG_LINUX_PATH, FZFG_WINDOWS_PATH
    import platform
    if platform.system() == "Linux" or platform.system() == "Darwin":
        script = FZFG_LINUX_PATH.read_text(encoding="utf-8")
    elif platform.system() == "Windows":
        script = FZFG_WINDOWS_PATH.read_text(encoding="utf-8")
    else:
        raise RuntimeError("Unsupported platform")
    if rga:
        script = script.replace("rg ", "rga ").replace("ripgrep", "ripgrep-all")
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=script, strict=False)


def main():
    app = typer.Typer(add_completion=False, no_args_is_help=True)
    app.command(name="msearch", help="machineconfig search helper", no_args_is_help=False)(machineconfig_search)
    app()
