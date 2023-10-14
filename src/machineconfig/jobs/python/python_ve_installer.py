
"""ve installer
"""

import crocodile.toolbox as tb
from machineconfig.utils.ve import get_ve_specs, get_installed_interpreters
import platform
# import machineconfig
from machineconfig.utils.utils import LIBRARY_ROOT as lib_root
from rich.panel import Panel
from rich.console import Console
# from rich.text import Text
# from typing import Any

system: str = platform.system()


def main():
    console = Console()
    print("\n\n")
    console.rule("Existing Python versions", style="bold red")
    res = get_installed_interpreters()
    tb.List(res).print()
    print("\n\n")

    console.rule(f"Existing virtual environments")
    for ve_path in tb.P.home().joinpath("venvs").search("*", files=False):
        ve_specs = get_ve_specs(ve_path)
        console.print(Panel(str(ve_specs), title=ve_path.stem, style="bold blue"))

    dotted_py_version = input("Enter python version (3.11): ") or "3.11"
    env_name = input("Enter virtual environment name (tst): ") or "tst"
    repos = input("Install essential repos? (y/[n]): ") or "n"

    env_path = tb.P.home().joinpath("venvs", env_name)
    if env_path.exists():
        console.rule(f"Deleting existing enviroment with similar name")
        env_path.delete(sure=True)

    scripts = lib_root.joinpath(f"setup_{system.lower()}/ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    variable_prefix = "$" if system == "Windows" else ""
    line1 = f"{variable_prefix}ve_name='{env_name}'"
    line2 = f"{variable_prefix}py_version='{dotted_py_version}'"
    lines = f"{line1}\n{line2}\n"
    line_start = "# --- Define ve name and python version here ---"
    line_end = "# --- End of user defined variables ---"
    assert line_start in scripts and line_end in scripts, "Script template was mutated beyond recognition."
    scripts = scripts.split(line_start)[0] + line_start + "\n" + lines + line_end + scripts.split(line_end)[1]
    if repos == "y":
        text = lib_root.joinpath(f"setup_{system.lower()}/repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
        text = tb.modify_text(txt_raw=text, txt_search="ve_name=", txt_alt=f"{variable_prefix}ve_name='{env_name}'", replace_line=True)
        scripts += text
    return scripts


if __name__ == '__main__':
    pass
