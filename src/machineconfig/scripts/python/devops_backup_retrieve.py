
"""BR: Backup and Retrieve
"""

# import subprocess
from crocodile.file_management import Read, P
from machineconfig.utils.utils import LIBRARY_ROOT, DEFAULTS_PATH, print_code, choose_cloud_interactively, choose_multiple_options
from machineconfig.scripts.python.cloud_sync import ES
from platform import system
from typing import Any, Literal, Optional


OPTIONS = Literal["BACKUP", "RETRIEVE"]


def main_backup_retrieve(direction: OPTIONS, which: Optional[str] = None):
    try:
        cloud: str = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        print(f"\n{'--' *  50}\n ⚠️ Using default cloud: `{cloud}` ⚠️\n{'--' *  50}\n")
    except (FileNotFoundError, KeyError, IndexError): cloud = choose_cloud_interactively()

    bu_file: dict[str, Any] = Read.toml(LIBRARY_ROOT.joinpath("profile/backup.toml"))
    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}

    if which is None:
        choices = choose_multiple_options(msg=f"WHICH FILE of the following do you want to {direction}?", options=['all'] + list(bu_file.keys()))
    else:
        choices = which.split(",") if isinstance(which, str) else which

    if "all" in choices: items = bu_file
    else:
        # items = {choices: bu_file[choices]}
        items = {key: val for key, val in bu_file.items() if key in choices}

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
        else:
            raise RuntimeError(f"Unknown direction: {direction}")
        if item_name == "dotfiles" and system() == "Linux": program += """\nchmod 700 ~/.ssh/*\n"""
    print_code(program, lexer="shell", desc=f"{direction} script")
    return program


def main(direction: OPTIONS, which: Optional[str] = None):
    code = main_backup_retrieve(direction=direction, which=which)
    from machineconfig.utils.utils import write_shell_script
    write_shell_script(program=code, desc="backup_retrieve.sh")


if __name__ == "__main__":
    pass
