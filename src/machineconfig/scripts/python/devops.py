
from platform import system
# import subprocess
import crocodile.toolbox as tb

PROGRAM_PATH = tb.P.tmp().joinpath("shells/python_return_command") + (".ps1" if system() == "Windows" else ".sh")

options = ['update essential repos',
           'install devapps',
           'install ve',
           'create symlinks',
           'add ssh key',
           'send ssh key',
           'setup ssh',
           'setup ssh wsl',
           'pull all repos',
           'commit all repos',
           'push all repos',
           'backup']


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

    if choice_key == "pull all repos":
        from machineconfig.jobs.python.repos import pull_all
        program = pull_all()

    elif choice_key == "push all repos":
        from machineconfig.jobs.python.repos import push_all
        program = push_all()

    elif choice_key == "commit all repos":
        from machineconfig.jobs.python.repos import commit_all
        program = commit_all()

    elif choice_key == "install ve":
        from machineconfig.jobs.python.python_ve_installer import ve_setup
        program = ve_setup()

    elif choice_key == "install devapps":
        if system() == "Windows":
            from machineconfig.jobs.python.python_windows_installers_all import get_installers
        else:
            from machineconfig.jobs.python.python_linux_installers_all import get_installers
        installers = get_installers()
        installers.list.insert(0, tb.P("all"))
        installers.print(styler=lambda x: x.stem)
        idx = int(input("\nChoose a program: "))
        if idx == 0:
            program_linux = "source ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh"
            program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1"
            program = program_linux if system() == "Linux" else program_windows
        else:
            installers[idx].readit()['main']()  # finish the task
            program = "echo 'Finished Installation'"  # write an empty program
    elif choice_key == "setup ssh":
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows
    elif choice_key == "setup ssh wsl":
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""
    elif choice_key == "update essential repos":
        program_windows = "~/code/machineconfig/src/machineconfig/jobs/windows/update_essentials.ps1"
        program_linux = "source ~/code/machineconfig/src/machineconfig/jobs/linux/update_essentials"
        program = program_linux if system() == "Linux" else program_windows
    elif choice_key == "install devapps":
        program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/devapps.ps1"
        program_linux = "source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)"
        program = program_linux if system() == "Linux" else program_windows
    elif choice_key == "create symlinks":
        program_windows = "~/code/machineconfig/src/machineconfig/setup_windows/symlinks.ps1"
        program_linux = "source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh"
        program = program_linux if system() == "Linux" else program_windows
    elif choice_key == "add ssh key":
        path_to_key = input("Path to ssh key: ")
        if system() == "Linux":
            program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
        else:  # Windows
            program_windows = "~/code/machineconfig/src/machineconfig/jobs/windows/openssh-server_add_key.ps1"
            program_windows = tb.P(program_windows).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')
            program = program_windows
    elif choice_key == "send ssh key":
        raise NotImplementedError
    elif choice_key == "backup":
        import machineconfig
        library_root = tb.P(machineconfig.__file__).parent.joinpath("profile/backup.toml").readit()
        for item_name, item in library_root.items():
            if system() == "Linux" and "windows" in item_name: continue
            if system() == "Windows" and "linux" in item_name: continue
            file = tb.P(item['path']).expanduser()
            onedrive = tb.P.home().joinpath("dotfiles/settings/paths.toml").readit()['onedrive']
            onedrive_name = onedrive[onedrive['default']]
            remote_dir = tb.P.home().joinpath(onedrive_name, f"myhome/{file.rel2home().parent}")
            if item['zip']: file = file.zip()
            if item['encrypt']: file = file.encrypt()
            file.move(folder=remote_dir)
        program = ""
    else:
        raise ValueError(f"Unimplemented choice: {choice_key}")

    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows':
        PROGRAM_PATH.create(parents_only=True).write_text(program)
    else:
        PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == "__main__":
    main()
