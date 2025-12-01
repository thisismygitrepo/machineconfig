"""Pure Python implementation for msearch command - no typer dependencies."""


def machineconfig_search(
    directory: str,
    ast: bool,
    symantic: bool,
    extension: str,
    file: bool,
    no_dotfiles: bool,
    rga: bool,
    install_dependencies: bool,
) -> None:
    """Machineconfig search helper."""
    if install_dependencies:
        _install_dependencies()
        return
    if symantic:
        _run_symantic_search(extension=extension)
        return
    if ast:
        _run_ast_search(directory=directory)
        return
    if file:
        _run_file_search(no_dotfiles=no_dotfiles)
        return
    _run_text_search(rga=rga)


def _install_dependencies() -> None:
    """Install required dependencies."""
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing
    install_if_missing("fzf")
    install_if_missing("tv")
    install_if_missing("bat")
    install_if_missing("fd")
    install_if_missing("rg")
    install_if_missing("rga")


def _run_symantic_search(extension: str) -> None:
    """Run symantic search."""
    script = ""
    for an_ex in extension.split(","):
        script = script + f"""\nparse *.{an_ex} """
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script)


def _run_ast_search(directory: str) -> None:
    """Run AST search."""
    from machineconfig.scripts.python.helpers.helpers_search.ast_search import get_repo_symbols
    symbols = get_repo_symbols(directory)
    from machineconfig.utils.options import choose_from_options
    try:
        res = choose_from_options(options=symbols, msg="Select a symbol to search for:", tv=True, multi=False)
        from rich import print_json
        import json
        res_json = json.dumps(res, indent=4)
        print_json(res_json)
    except Exception as e:
        print(f"❌ Error during selection: {e}")


def _run_file_search(no_dotfiles: bool) -> None:
    """Run file search."""
    script = """fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}' """
    if no_dotfiles:
        script = "fd | " + script
    from machineconfig.utils.code import run_shell_script
    run_shell_script(script=script)


def _run_text_search(rga: bool) -> None:
    """Run text search using fzf with ripgrep."""
    from machineconfig.scripts.python.helpers.helpers_msearch import FZFG_LINUX_PATH, FZFG_WINDOWS_PATH
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
