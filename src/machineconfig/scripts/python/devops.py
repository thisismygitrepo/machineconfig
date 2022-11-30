
from platform import system
# import subprocess
import crocodile.toolbox as tb

PROGRAM_PATH = tb.P.tmp().joinpath("shells/python_return_command") + (".ps1" if system() == "Windows" else ".sh")

options = ['UPDATE essential repos',
           'DEVAPPS install',
           'VE install',
           'SYMLINKS creation',
           'SSH add pub key to this machine',
           'SSH send pub key to a machine',
           'SSH setup',
           'SSH setup wsl',
           'REPOS pull all',
           'REPOS commit all',
           'REPOS push all',
           'BACKUP']


def main():
    PROGRAM_PATH.delete(sure=True, verbose=False)

    print("\n")
    print(f"DEVOPS".center(50, "-"))
    for idx, key in enumerate(options):
        print(idx, key)
    print("\n")
    choice_idx = input("Enter a number: ")
    try:
        choice_key = options[int(choice_idx)]
    except IndexError:
        raise ValueError(f"Unknown choice. {choice_idx}")
    print(f"{choice_key}".center(50, "-"))

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
        installers.print(styler=lambda x: x.stem)
        idx = int(input("\nChoose a program by index: "))
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

    elif choice_key == "SSH setup":
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH setup wsl":
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == "SSH add pub key to this machine":

        from machineconfig.scripts.python.devops_add_ssh_key import get_add_ssh_key_script
        path_to_key = input("Path to public key or paste public key or press enter to add all .pub keys in ~/.ssh : ")
        if path_to_key == "":
            programs = tb.P.home().joinpath(".ssh").search("*.pub").apply(get_add_ssh_key_script)
            program = "\n\n\n".join(programs)
        else:
            path_to_key = tb.P(path_to_key).expanduser().absolute()
            if path_to_key.exists(): pass
            else: path_to_key = tb.P.home().joinpath(".ssh/my_pasted_key.pub").write_text(path_to_key.str)
            program = get_add_ssh_key_script(path_to_key)

    elif choice_key == "SSH send pub key to a machine":
        raise NotImplementedError
    elif choice_key == "BACKUP":
        for item_name, item in get_res().items():
            if system() == "Linux" and "windows" in item_name: continue
            if system() == "Windows" and "linux" in item_name: continue
            file = tb.P(item['path']).expanduser()
            onedrive = tb.P.home().joinpath("dotfiles/settings/paths.toml").readit()['onedrive']
            onedrive_name = onedrive[onedrive['default']]
            remote_dir = tb.P.home().joinpath(onedrive_name, f"myhome/{file.rel2home().parent}")
            if item['zip']: file = file.zip()
            if item['encrypt']: file = file.encrypt()
            file.move(folder=remote_dir, overwrite=True)
        program = "echo 'Finished Backing up.'"
    elif choice_key == "retrieve":
        for item_name, item in get_res().items():
            if system() == "Linux" and "windows" in item_name: continue
            if system() == "Windows" and "linux" in item_name: continue
            file = tb.P(item['path']).expanduser()
            onedrive = tb.P.home().joinpath("dotfiles/settings/paths.toml").readit()['onedrive']
            onedrive_name = onedrive[onedrive['default']]
            remote_dir = tb.P.home().joinpath(onedrive_name, f"myhome/{file.rel2home()}")
            file = remote_dir.move(folder=file.parent, overwrite=True)
            if item['encrypt']: file = file.decrypt()
            if item['zip']: file = file.unzip()
            _ = file
        program = "echo 'Finished retrieving up.'"
    else:
        raise ValueError(f"Unimplemented choice: {choice_key}")

    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows':
        PROGRAM_PATH.create(parents_only=True).write_text(program)
    else:
        PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


def get_res():
    import machineconfig
    library_root = tb.P(machineconfig.__file__).parent.joinpath("profile/backup.toml").readit()
    choices_list = ['all'] + tb.L(library_root.keys())
    choices_list.print()
    choice_number = int(input("Choose a backup: "))
    if choice_number == 0:
        res = library_root
    else:
        choice_entry = tb.L(library_root.keys())[choice_number]
        res = {choice_entry: library_root[choice_entry]}
    return res


if __name__ == "__main__":
    main()
