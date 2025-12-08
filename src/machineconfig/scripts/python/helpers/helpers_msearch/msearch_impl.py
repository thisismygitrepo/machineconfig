"""Pure Python implementation for msearch command - no typer dependencies."""


from typing import Optional


def machineconfig_search(
    path: str, ast: bool, symantic: bool, extension: str, file: bool, no_dotfiles: bool, rga: bool, install_dependencies: bool
) -> None:
    """Machineconfig search helper."""
    

    if install_dependencies:
        _install_dependencies()
        return
    if symantic:
        _run_symantic_search(extension=extension)
        return
    if ast:
        _run_ast_search(directory=path)
        return
    if file:
        _run_file_search(no_dotfiles=no_dotfiles)
        return

    from pathlib import Path
    import platform
    import sys
    import tempfile
    import io
    is_temp_file = False
    if not sys.stdin.isatty() and Path(path).is_dir():
        # Use UTF-8 encoding to handle emoji and Unicode characters on Windows
        if sys.stdin.encoding != 'utf-8':
            stdin_wrapper = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
            content = stdin_wrapper.read()
        else:
            content = sys.stdin.read()
        if content:
            tf = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, prefix="msearch_stdin_")
            tf.write(content)
            tf.close()
            path = tf.name
            is_temp_file = True

    if Path(path).is_file():
        from machineconfig.utils.code import exit_then_run_shell_script
        abs_path = str(Path(path).absolute())
        if platform.system() == "Linux" or platform.system() == "Darwin":
            code = """
nl -ba -w1 -s' ' "$TEMP_FILE" | tv \
    --preview-command "bat --color=always --highlight-line {split: :0} $TEMP_FILE" \
    --preview-size 80 \
    --preview-offset "{split: :0}" \
    --source-output "{}" \
    | cut -d' ' -f2-
"""
            code = code.replace("$TEMP_FILE", abs_path)
            if is_temp_file:
                code += f"\nrm {path}"
            exit_then_run_shell_script(script=code, strict=False)
            return
        elif platform.system() == "Windows":
            # PowerShell equivalent: number lines, pipe to tv, extract content after line number
            # IMPORTANT: Use -join to create a single string before piping to tv
            # PowerShell enumerates collections when piping to native commands, treating each
            # line as a separate argument. Using -join ensures tv receives a single stdin stream.
            abs_path_escaped = abs_path.replace("'", "''")
            code = f"""
$numbered = @(); $i=0; Get-Content '{abs_path_escaped}' | ForEach-Object {{ $numbered += "$((++$i)) $_" }}
($numbered -join "`n") | tv `
    --preview-command "bat --color=always --highlight-line {{split: :0}} '{abs_path_escaped}'" `
    --preview-size 80 `
    --preview-offset "{{split: :0}}" `
    --source-output "{{}}" | ForEach-Object {{ $_ -replace '^\\d+\\s+', '' }}
"""
            if is_temp_file:
                code += f"\nRemove-Item '{abs_path_escaped}' -Force"
            exit_then_run_shell_script(script=code, strict=False)
            return
    _run_text_search(rga=rga, directory=None)


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


def _run_text_search(rga: bool, directory: Optional[str]) -> None:
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
    if directory:
        script = "cd " + directory + "\n" + script
    exit_then_run_shell_script(script=script, strict=False)
