
import typer


def machineconfig_lf():
    # from machineconfig.scripts.python.helpers_msearch import FZFG_LINUX_PATH, FZFG_WINDOWS_PATH
    import platform
    if platform.system() == "Linux":
        script = """
tmp="$(mktemp)"
lf -last-dir-path="$tmp" "$@"
if [ -f "$tmp" ]; then
    dir="$(cat "$tmp")"
    rm -f "$tmp"
    if [ -d "$dir" ]; then
        if [ "$dir" != "$(pwd)" ]; then
            cd "$dir"
        fi
    fi
fi
"""
    elif platform.system() == "Windows":
        script = r"""
$tmp = [System.IO.Path]::GetTempFileName()
~\AppData\Local\Microsoft\WindowsApps\lf.exe -last-dir-path="$tmp" $args
if (Test-Path -PathType Leaf "$tmp")
{
    $dir = Get-Content "$tmp"
    Remove-Item -Force "$tmp"
    if (Test-Path -PathType Container "$dir")
    {
        if ("$dir" -ne "$pwd")
        {
            Set-Location "$dir"
        }
    }
}
"""
    else:
        raise RuntimeError("Unsupported platform")

    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(script=script, strict=False)


def main():
    app = typer.Typer(add_completion=False, no_args_is_help=True)
    app.command(name="lf", help="machineconfig lf wrapper.", no_args_is_help=False)(machineconfig_lf)
    app()
