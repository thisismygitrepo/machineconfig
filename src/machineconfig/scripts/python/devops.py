
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
           'SSH add identity to this machine',
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
            program_linux = "source ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh"
            program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1"
            program = program_linux if system() == "Linux" else program_windows
        else:
            program = installers[idx].readit()['main']()  # finish the task
            if program is None: program = "echo 'Finished Installation'"  # write an empty program

    elif choice_key == "UPDATE essential repos":
        program_windows = "~/code/machineconfig/src/machineconfig/jobs/windows/update_essentials.ps1"
        program_linux = "source ~/code/machineconfig/src/machineconfig/jobs/linux/update_essentials"
        if tb.P.home().joinpath("code/crocodile").expanduser().exists():
            program = program_linux if system() == "Linux" else program_windows
        else:
            program = "pip install --upgrade crocodile; pip install --upgrade machineconfig"

    elif choice_key == "DEVAPPS install":
        program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1"
        program_linux = "source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)"
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SYMLINKS creation":
        program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1"
        program_linux = "source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh"
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH add pub key to this machine":

        from machineconfig.scripts.python.devops_add_ssh_key import get_add_ssh_key_script
        path_to_key = input("Path to public key or paste public key or press enter to add all .pub keys in ~/.ssh : ")
        if path_to_key == "":
            programs = tb.P.home().joinpath(".ssh").search("*.pub")
            print(f"Adding the keys\n {programs.print()}")
            program = "\n\n\n".join(programs.apply(get_add_ssh_key_script))
        else:
            tmp = tb.P(path_to_key).expanduser().absolute()
            if tmp.exists(): path_to_key = tmp
            else: path_to_key = tb.P.home().joinpath(".ssh/my_pasted_key.pub").write_text(path_to_key)
            program = get_add_ssh_key_script(path_to_key)

    elif choice_key == "SSH send pub key to a machine":
        raise NotImplementedError

    elif choice_key == 'SSH add identity (private key) to this machine':
        path_to_key = input("Path to private key to be used when ssh'ing: ")
        path_to_key = tb.P(path_to_key).expanduser().absolute()
        if system() == 'Windows':
            program = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add_identity.ps1").read_text()
            program = program.replace(r'$sshfile = "$env:USERPROFILE\.ssh\id_rsa"', f'$sshfile = "{path_to_key}"')
        else: raise NotImplementedError

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
