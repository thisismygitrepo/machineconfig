
from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def main():
    direction = display_options(msg="BACKUP OR RETRIEVE?", options=["BACKUP", "RETRIEVE"], default="BACKUP")
    drive = display_options(msg="WHICH CLOUD?", options=["GDrive", "OneDrive"], default="OneDrive")
    bu_file = LIBRARY_ROOT.joinpath("profile/backup.toml").readit()
    if system() == "Linux": bu_file = {key: val for key, val in bu_file.items() if "windows" not in key}
    elif system() == "Windows": bu_file = {key: val for key, val in bu_file.items() if "linux" not in key}
    choice_key = display_options(msg="WHICH FILE of the following do you want to back up?", options=['all'] + list(bu_file.keys()), default="dotfiles")
    if choice_key == "all": items = list(bu_file.values())
    else: items = [bu_file[choice_key]]

    if direction == "BACKUP" and drive == "OneDrive":
        from machineconfig.scripts.python.bu_onedrive_sx import main
        for item in items: main(which="default", zip_first=item['zip'], encrypt_first=item['encrypt'], file=tb.P(item['path']).expanduser(), key=None, pwd=None, overwrite=True)
    elif direction == "RETRIEVE" and drive == "OneDrive":
        from machineconfig.scripts.python.bu_onedrive_rx import main
        for item in items: main(which="default", unzip=item['zip'], decrypt=item['encrypt'], file=tb.P(item['path']).expanduser(), overwrite=True, key=None, pwd=None)
    elif direction == "BACKUP" and drive == "GDrive":
        from machineconfig.scripts.python.bu_gdrive_sx import main
        for item in items: main(google_account=None, project=None, zip_first=item['zip'], encrypt_first=item['encrypt'], file=tb.P(item['path']).expanduser(), relative_to_home=True, remote_dir="", share=False, key=None, pwd=None)
    elif direction == "RETRIEVE" and drive == "GDrive":
        from machineconfig.scripts.python.bu_gdrive_rx import main
        for item in items: main(google_account=None, project=None, unzip=item['zip'], decrypt=item['encrypt'], file=tb.P(item['path']).expanduser(), relative_to_home=True, local_dir="", key=None, pwd=None)
    else: raise ValueError
    program = f"echo 'Finished backing up {items}.'"

    return program


if __name__ == "__main__":
    pass
