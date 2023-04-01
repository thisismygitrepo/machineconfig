
from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options, print_programming_script


def main():
    direction = display_options(msg="BACKUP OR RETRIEVE?", options=["BACKUP", "RETRIEVE"], default="BACKUP", fzf=True)
    tool = "cloud_sx" if direction == "BACKUP" else "cloud_rx"

    remotes = tb.L(tb.Terminal().run("rclone listremotes", shell="pwsh").op_if_successfull_or_default("").splitlines()).apply(lambda x: x.replace(":", ""))
    if len(remotes) == 0:
        raise RuntimeError(f"You don't have remotes. Configure your rclone first to get cloud services access.")
    cloud = display_options(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0], fzf=True)

    bu_file = LIBRARY_ROOT.joinpath("profile/backup.toml").readit()

    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}

    # choice_key = display_options(msg="WHICH FILE of the following do you want to back up?", options=['all'] + list(bu_file.keys()), default="dotfiles")
    #
    # if choice_key == "all": items = bu_file
    # else: items = {choice_key: bu_file[choice_key]}
    items = bu_file

    program = f"""
$cloud="{cloud}"
"""
    for item_name, item in items.items():
        path = tb.P(item['path'])
        os_specific = True if system().lower() in item_name else False
        flags = ''
        flags += 'z' if item['zip'] else ''
        flags += 'e' if item['encrypt'] else ''
        flags += 'r'
        flags += 'o' if os_specific else ''
        if flags: flags = f"-{flags}"
        program += f"""\n{tool} "{path.as_posix()}" --cloud $cloud {flags}\n"""
        if item_name == "dotfiles" and system() == "Linux": program += f"""\nchmod 700 ~/.ssh/*\n"""
    print_programming_script(program, lexer="shell", desc=f"{direction} script")
    print(program)


if __name__ == "__main__":
    pass
