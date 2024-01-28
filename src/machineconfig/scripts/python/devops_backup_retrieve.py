
"""BR: Backup and Retrieve
"""

# import subprocess
from crocodile.file_management import Read, P
from machineconfig.utils.utils import LIBRARY_ROOT, DEFAULTS_PATH, print_code, choose_cloud_interactively, display_options
from machineconfig.scripts.python.cloud_sync import ES
from platform import system
from typing import Any, Literal, Optional


OPTIONS = Literal["BACKUP", "RETRIEVE"]


def main(direction: OPTIONS, which: Optional[str] = None):
    try:
        cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        print(f"\n{'--' *  50}\n ⚠️ Using default cloud: `{cloud}` ⚠️\n{'--' *  50}\n")
    except (FileNotFoundError, KeyError, IndexError): cloud = choose_cloud_interactively()

    bu_file: dict[str, Any] = LIBRARY_ROOT.joinpath("profile/backup.toml").readit()
    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}

    if which is None:
        choice_key = display_options(msg=f"WHICH FILE of the following do you want to {direction}?", options=['all'] + list(bu_file.keys()))
        assert isinstance(choice_key, str)
    else: choice_key = which

    if choice_key == "all": items = bu_file
    else: items = {choice_key: bu_file[choice_key]}

    program = f"""$cloud = "{cloud}:{ES}" \n """ if system() == "Windows" else f"""cloud="{cloud}:{ES}" \n """
    for item_name, item in items.items():
        # P.home().joinpath(".ipython").to_cloud(cloud="oduq1", zip=True, encrypt=True, rel2home=True, os_specific=False)
        flags = ''
        flags += 'z' if item['zip'] == 'True' else ''
        flags += 'e' if item['encrypt'] == 'True' else ''
        flags += 'r' if item['rel2home'] == 'True' else ''
        flags += 'o' if system().lower() in item_name else ''
        if flags: flags = "-" + flags
        if direction == "BACKUP": program += f"""\ncloud_copy "{P(item['path']).as_posix()}" $cloud {flags}\n"""
        elif direction == "RETRIEVE": program += f"""\ncloud_copy $cloud "{P(item['path']).as_posix()}" {flags}\n"""
        else: raise RuntimeError(f"Unknown direction: {direction}")
        if item_name == "dotfiles" and system() == "Linux": program += f"""\nchmod 700 ~/.ssh/*\n"""
    print_code(program, lexer="shell", desc=f"{direction} script")
    return program


if __name__ == "__main__":
    pass
