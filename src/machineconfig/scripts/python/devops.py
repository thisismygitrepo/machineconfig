
from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


PROGRAM_PATH = tb.P.tmp().joinpath("shells/python_return_command") + (".ps1" if system() == "Windows" else ".sh")


options = ['UPDATE essential repos',
           'DEVAPPS install',
           'VE install',
           'SYMLINKS creation',
           'SSH add pub key to this machine',
           'SSH send pub key to a machine',
           'SSH add identity (private key) to this machine',
           'SSH setup',
           'SSH setup wsl',
           'REPOS pull all',
           'REPOS commit all',
           'REPOS push all',
           'BACKUP & RETRIEVE']


def main():
    PROGRAM_PATH.delete(sure=True, verbose=False)
    choice_key = display_options(msg="", options=options, header="DEVOPS", default=options[0])

    if choice_key == "REPOS pull all":
        from machineconfig.jobs.python.repos import pull_all
        program = pull_all()

    elif choice_key == "REPOS push all":
        from machineconfig.jobs.python.repos import push_all
        program = push_all()

    elif choice_key == "REPOS commit all":
        from machineconfig.jobs.python.repos import commit_all
        program = commit_all()

    elif choice_key == "VE install":
        from machineconfig.jobs.python.python_ve_installer import ve_setup
        program = ve_setup()

    elif choice_key == "DEVAPPS install":
        if system() == "Windows":
            from machineconfig.jobs.python.python_windows_installers_all import get_installers
        else:
            from machineconfig.jobs.python.python_linux_installers_all import get_installers
        installers = get_installers()
        installers.list.insert(0, tb.P("all"))
        idx = display_options(msg="", options=installers.stem, header="CHOOSE DEV APP")
        if idx == 0:
            program_linux = f"source {LIBRARY_ROOT}/setup_linux/devapps.sh"
            program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
            program = program_linux if system() == "Linux" else program_windows
        else:
            program = installers[idx].readit()['main']()  # finish the task
            if program is None: program = "echo 'Finished Installation'"  # write an empty program

    elif choice_key == "UPDATE essential repos":
        program_windows = f"{LIBRARY_ROOT}/jobs/windows/update_essentials.ps1"
        program_linux = f"source {LIBRARY_ROOT}/jobs/linux/update_essentials"
        if tb.P.home().joinpath("code/crocodile").expanduser().exists():
            program = program_linux if system() == "Linux" else program_windows
        else:
            program = "pip install --upgrade crocodile; pip install --upgrade machineconfig"

    elif choice_key == "DEVAPPS install":
        program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
        program_linux = f"source <(sudo cat {LIBRARY_ROOT}/setup_linux/devapps.sh)"
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SYMLINKS creation":
        program_windows = f"{LIBRARY_ROOT}/setup_windows/symlinks.ps1"
        program_linux = f"source {LIBRARY_ROOT}/setup_linux/symlinks.sh"
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH add pub key to this machine":
        from machineconfig.scripts.python.devops_add_ssh_key import get_add_ssh_key_script
        pub_keys = tb.P.home().joinpath(".ssh").search("*.pub")
        res = display_options("Which public key to add? ", options=pub_keys.list + ["all", "I have the path to the key file", "I want to paste the key itself"])
        if res == "all": program = "\n\n\n".join(pub_keys.apply(get_add_ssh_key_script))
        elif res == "I have the path to the key file": program = get_add_ssh_key_script(tb.P(input("Path: ")).expanduser().absolute())
        elif res == "I want to paste the key itself": program = get_add_ssh_key_script(tb.P.home().joinpath(f".ssh/{input('file name (default: my_pasted_key.pub): ') or 'my_pasted_key.pub'}").write_text(input("Paste the pub key here: ")))
        else: program = get_add_ssh_key_script(tb.P(res))

    elif choice_key == "SSH send pub key to a machine":
        raise NotImplementedError

    elif choice_key == 'SSH add identity (private key) to this machine':  # so that you can SSH directly withuot pointing to identity key.
        private_keys = tb.P.home().joinpath(".ssh").search("*.pub").apply(lambda x: x.with_name(x.stem)).filter(lambda x: x.exists())
        choice = display_options(msg="Path to private key to be used when ssh'ing: ", options=private_keys.list + ["I have the path to the key file", "I want to paste the key itself"])
        if choice == "I have the path to the key file": path_to_key = tb.P(input("Input path here: ")).expanduser().absolute()
        elif choice == "I want to paste the key itself": path_to_key = tb.P.home().joinpath(f".ssh/{input('file name (default: my_pasted_key): ') or 'my_pasted_key'}").write_text(input("Paste the private key here: "))
        else: path_to_key = tb.P(choice)
        txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"  # adds this id for all connections, no host specified.
        config_path = tb.P.home().joinpath(".ssh/config")
        if config_path.exists(): config_path.modify_text(txt=txt, alt=txt, newline=True, notfound_append=True, prepend=True)  # note that Identity line must come on top of config file otherwise it won't work, hence `prepend=True`
        else: config_path.write_text(txt)
        program = f"echo 'Finished adding identity to ssh config file. {'*'*50} Consider reloading config file.'"

    elif choice_key == "SSH setup":
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH setup wsl":
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == "BACKUP & RETRIEVE":
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
            for item in items: main(which="default", zip_first=item['zip'], encrypt_first=item['encrypt'], file=tb.P(item['path']).expanduser(), key=None, pwd=None)
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
    else:
        raise ValueError(f"Unimplemented choice: {choice_key}")

    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows':
        PROGRAM_PATH.create(parents_only=True).write_text(program)
    else:
        PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == "__main__":
    main()
