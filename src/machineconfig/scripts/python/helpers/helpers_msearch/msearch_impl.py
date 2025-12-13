"""Pure Python implementation for msearch command - no typer dependencies."""


from typing import Optional


def machineconfig_search(
    path: str, ast: bool, symantic: bool, extension: str, file: bool, no_dotfiles: bool, rga: bool, edit: bool, install_dependencies: bool
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
        _run_file_search(no_dotfiles=no_dotfiles, edit=edit)
        return

    from pathlib import Path
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

    if Path(path).absolute().resolve().is_file():
        from machineconfig.utils.code import exit_then_run_shell_script
        code = search_file_with_context(path=path, is_temp_file=is_temp_file, edit=edit)
        exit_then_run_shell_script(script=code, strict=False)
        return

    _run_text_search(rga=rga, directory=path)


def _install_dependencies() -> None:
    """Install required dependencies."""
    from machineconfig.utils.installer_utils.installer_cli import install_if_missing

    install_if_missing("fzf")
    install_if_missing("tv")
    install_if_missing("bat")
    install_if_missing("fd")
    install_if_missing("rg")
    install_if_missing("rga")



def search_file_with_context(path: str, is_temp_file: bool, edit: bool) -> str:
    import platform
    import base64
    from pathlib import Path
    abs_path = str(Path(path).absolute())
    if platform.system() == "Linux" or platform.system() == "Darwin":
        if edit:
            code = """
res=$(nl -ba -w1 -s' ' "$TEMP_FILE" | tv \
--preview-command "bat --color=always --style=numbers --highlight-line {split: :0} $TEMP_FILE" \
--preview-size 80 \
--preview-offset "{split: :0}" \
--source-output "{}")
if [ -n "$res" ]; then
    line=$(echo "$res" | cut -d' ' -f1)
    hx "$TEMP_FILE:$line"
fi
"""
        else:
            code = """
nl -ba -w1 -s' ' "$TEMP_FILE" | tv \
--preview-command "bat --color=always --style=numbers --highlight-line {split: :0} $TEMP_FILE" \
--preview-size 80 \
--preview-offset "{split: :0}" \
--source-output "{}" \
| cut -d' ' -f2-
"""
        code = code.replace("$TEMP_FILE", abs_path)
        if is_temp_file:
            code += f"\nrm {path}"
    elif platform.system() == "Windows":
        # Windows: avoid piping INTO `tv` (it breaks TUI interactivity on Windows terminals).
        # Use `tv --source-command` so stdin remains attached to the console.
        # Note: using `cmd /C type` here has proven brittle due to quoting/command-line parsing
        # differences; generate the numbered lines via a self-contained PowerShell command.
        abs_path_escaped = abs_path.replace("'", "''")
        # Use `-EncodedCommand` to avoid nested quoting issues across PowerShell/tv/cmd.
        ps_script = (
            "$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
            "$i = 0; "
            f"Get-Content -LiteralPath '{abs_path_escaped}' | ForEach-Object {{ $i = $i + 1; \"{{0}} {{1}}\" -f $i, $_ }}"
        )
        encoded = base64.b64encode(ps_script.encode("utf-16le")).decode("ascii")
        source_cmd = f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"
        source_cmd_ps_literal = source_cmd.replace("'", "''")
        if edit:
            code = f"""
$sourceCmd = '{source_cmd_ps_literal}'
$res = tv `
--source-command $sourceCmd `
--preview-command 'bat --color=always --style=numbers --highlight-line {{split: :0}} {abs_path}' `
--preview-size 80 `
--preview-offset "{{split: :0}}" `
--source-output "{{}}"
if ($res) {{
    $line = $res.Split(' ')[0]
    hx "{abs_path_escaped}:$line"
}}
"""
        else:
            code = f"""
$sourceCmd = '{source_cmd_ps_literal}'
tv `
--source-command $sourceCmd `
--preview-command 'bat --color=always --style=numbers --highlight-line {{split: :0}} {abs_path}' `
--preview-size 80 `
--preview-offset "{{split: :0}}" `
--source-output "{{}}" | ForEach-Object {{ $_ -replace '^\\d+\\s+', '' }}
"""
        if is_temp_file:
            code += f"\nRemove-Item '{abs_path_escaped}' -Force"
    else:
        raise RuntimeError(f"Unsupported platform, {platform.system()}")
    return code

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


def _run_file_search(no_dotfiles: bool, edit: bool) -> None:
    """Run file search."""
    import platform

    if not edit:
        script = """fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}' """
        if no_dotfiles:
            script = "fd | " + script
        from machineconfig.utils.code import run_shell_script

        run_shell_script(script=script)
        return

    if platform.system() == "Linux" or platform.system() == "Darwin":
        script = """
selected=$({SOURCE_CMD} fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}')
if [ -n "$selected" ]; then
    res=$(nl -ba -w1 -s' ' "$selected" | tv \
    --preview-command "bat --color=always --style=numbers --highlight-line {split: :0} $selected" \
    --preview-size 80 \
    --preview-offset "{split: :0}" \
    --source-output "{}")
    if [ -n "$res" ]; then
        line=$(echo "$res" | cut -d' ' -f1)
        hx "$selected:$line"
    fi
fi
"""
        source_cmd = "" if not no_dotfiles else "fd | "
        script = script.replace("{SOURCE_CMD}", source_cmd)
    elif platform.system() == "Windows":
        script = r"""
$selected = {SOURCE_CMD} fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}'
if ($selected) {
    $choicesPath = Join-Path $env:TEMP ("msearch_choices_" + [guid]::NewGuid().ToString() + ".txt")
    $i = 0
    Get-Content -LiteralPath "$selected" | ForEach-Object { $i = $i + 1; "{0} {1}" -f $i, $_ } | Set-Content -LiteralPath $choicesPath -Encoding utf8
    $sourceCmd = 'cmd /C type "' + $choicesPath + '"'
    $previewCmd = 'bat --color=always --style=numbers --highlight-line {split: :0} "' + $selected + '"'
    $res = tv `
    --source-command $sourceCmd `
    --preview-command $previewCmd `
    --preview-size 80 `
    --preview-offset "{split: :0}" `
    --source-output "{}"
    Remove-Item -LiteralPath $choicesPath -Force -ErrorAction SilentlyContinue
    if ($res) {
        $line = $res.Split(' ')[0]
        hx "$($selected):$line"
    }
}
"""
        source_cmd = "" if not no_dotfiles else "fd | "
        script = script.replace("{SOURCE_CMD}", source_cmd)
    else:
        raise RuntimeError("Unsupported platform")

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
