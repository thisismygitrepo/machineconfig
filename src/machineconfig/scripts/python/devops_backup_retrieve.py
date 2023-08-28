
"""BR: Backup and Retrieve
"""

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options, print_programming_script


def main():
    direction = display_options(msg="BACKUP OR RETRIEVE?", options=["BACKUP", "RETRIEVE"], default="BACKUP", fzf=True)

    print(f"Listing Remotes ... ")
    tmp = tb.Terminal().run("rclone listremotes", shell="pwsh").op_if_successfull_or_default(strict_returcode=False)
    if isinstance(tmp, str):
        remotes = tb.L(tmp.splitlines()).apply(lambda x: x.replace(":", ""))
    else: raise ValueError(f"Got {tmp} from rclone listremotes")
    if len(remotes) == 0:
        raise RuntimeError(f"You don't have remotes. Configure your rclone first to get cloud services access.")
    cloud = display_options(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0], fzf=True)

    bu_file = LIBRARY_ROOT.joinpath("profile/backup.toml").readit()

    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}

    # choice_key = display_options(msg="WHICH FILE of the following do you want to back up?", options=['all'] + list(bu_file.keys()), default="dotfiles")
    # if choice_key == "all": items = bu_file
    # else: items = {choice_key: bu_file[choice_key]}
    items = bu_file

    program = f"""$cloud = "{cloud}:" \n """ if system() == "Windows" else f"""cloud="{cloud}:" \n """
    for item_name, item in items.items():
        path = tb.P(item['path'])
        os_specific = True if system().lower() in item_name else False
        flags = ''
        flags += 'z' if item['zip'] else ''
        flags += 'e' if item['encrypt'] else ''
        flags += 'r'
        flags += 'o' if os_specific else ''
        if flags: flags = f"-{flags}"
        if direction == "BACKUP":
            program += f"""\ncloud_copy "{path.as_posix()}" $cloud {flags}\n"""
        elif direction == "RETRIEVE":
            program += f"""\ncloud_copy $cloud "{path.as_posix()}" {flags}\n"""
        else: raise RuntimeError(f"Unknown direction: {direction}")
        if item_name == "dotfiles" and system() == "Linux": program += f"""\nchmod 700 ~/.ssh/*\n"""
    program += f"""\ncd ~/dotfiles; cloud_repo_sync --cloud {cloud}\n"""
    print_programming_script(program, lexer="shell", desc=f"{direction} script")
    print(program)
    return ""


if __name__ == "__main__":
    pass
