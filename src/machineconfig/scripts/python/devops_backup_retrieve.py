
from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def main():
    direction = display_options(msg="BACKUP OR RETRIEVE?", options=["BACKUP", "RETRIEVE"], default="BACKUP")

    remotes = tb.L(tb.Terminal().run("rclone listremotes", shell="pwsh").op_if_successfull_or_default("").splitlines()).apply(lambda x: x.replace(":", ""))
    cloud = display_options(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0])
    bu_file = LIBRARY_ROOT.joinpath("profile/backup.toml").readit()
    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}
    choice_key = display_options(msg="WHICH FILE of the following do you want to back up?", options=['all'] + list(bu_file.keys()), default="dotfiles")
    if choice_key == "all": items = list(bu_file.values())
    else: items = [bu_file[choice_key]]

    for item in items:
        tb.S(item).print(as_config=True, title=direction)
        if direction == "BACKUP": tb.P(item['path']).to_cloud(cloud=cloud, zip=item['zip'], rel2home=True, encrypt=item['encrypt'], key=None, pwd=None)
        elif direction == "RETRIEVE": tb.P(item['path']).from_cloud(cloud=cloud, unzip=item['zip'], rel2home=True, decrypt=item['encrypt'], localpath=None, key=None, pwd=None)
        else: raise ValueError

    program = f"echo 'Finished backup.'"

    return program


if __name__ == "__main__":
    pass
