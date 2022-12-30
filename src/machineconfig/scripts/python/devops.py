
from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


PROGRAM_PATH = tb.P.tmp().joinpath("shells/python_return_command") + (".ps1" if system() == "Windows" else ".sh")


options = ['UPDATE essential repos',
           'DEVAPPS install',
           'VE install',
           'SYMLINKS new',
           'SYMLINKS creation',
           'SSH add pub key to this machine',
           'SSH add identity (private key) to this machine',
           'SSH use key pair to connect two machines',
           'SSH setup',
           'SSH setup wsl',
           'REPOS pull all',
           'REPOS commit all',
           'REPOS push all',
           'BACKUP & RETRIEVE']


def main():
    PROGRAM_PATH.delete(sure=True, verbose=False)
    choice_key = display_options(msg="", options=options, header="DEVOPS", default=options[0])

    if choice_key == "UPDATE essential repos":
        import machineconfig.scripts.python.devops_update_repos as helper
        program = helper.main()

    elif choice_key == "VE install":
        from machineconfig.jobs.python.python_ve_installer import main
        program = main()

    elif choice_key == "DEVAPPS install":
        from machineconfig.scripts.python.devops_devapps_install import main
        program = main()

    elif choice_key == "SYMLINKS new":
        from machineconfig.jobs.python.python_ve_symlink import main
        program = main()

    elif choice_key == "SYMLINKS creation":
        program_windows = f"{LIBRARY_ROOT}/setup_windows/symlinks.ps1"
        program_linux = f"source {LIBRARY_ROOT}/setup_linux/symlinks.sh"
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH add pub key to this machine":
        from machineconfig.scripts.python.devops_add_ssh_key import main
        program = main()

    elif choice_key == "SSH use key pair to connect two machines":
        raise NotImplementedError

    elif choice_key == 'SSH add identity (private key) to this machine':  # so that you can SSH directly withuot pointing to identity key.
        from machineconfig.scripts.python.devops_add_identity import main
        program = main()

    elif choice_key == "SSH setup":
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == "SSH setup wsl":
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == "BACKUP & RETRIEVE":
        from machineconfig.scripts.python.devops_backup_retrieve import main
        program = main()

    elif choice_key == "REPOS pull all":
        from machineconfig.jobs.python.repos import pull_all
        program = pull_all()

    elif choice_key == "REPOS push all":
        from machineconfig.jobs.python.repos import push_all
        program = push_all()

    elif choice_key == "REPOS commit all":
        from machineconfig.jobs.python.repos import commit_all
        program = commit_all()

    else:
        raise ValueError(f"Unimplemented choice: {choice_key}")

    print(f"Executing {PROGRAM_PATH}")
    if system() == 'Windows':
        PROGRAM_PATH.create(parents_only=True).write_text(program)
    else:
        PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")


if __name__ == "__main__":
    main()
