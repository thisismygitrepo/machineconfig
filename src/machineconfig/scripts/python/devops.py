
from platform import system
# import subprocess
# import crocodile.toolbox as tb
from machineconfig.utils.utils import display_options, PROGRAM_PATH, write_shell_script
from enum import Enum


# needs to be synced with devops.sh and devops.ps1


class Options(Enum):
    update         = 'UPDATE essential repos'
    devaps         = 'DEVAPPS install'
    ve             = 'VE install'
    sym_path_shell = 'SYMLINKS, PATH & SHELL PROFILE'
    sym_new        = 'SYMLINKS new'
    ssh_add_pubkey = 'SSH add pub key to this machine'
    ssh_add_id     = 'SSH add identity (private key) to this machine'
    ssh_use_pair   = 'SSH use key pair to connect two machines'
    ssh_setup      = 'SSH setup'
    ssh_setup_wsl  = 'SSH setup wsl'
    # repos_pull     = 'REPOS pull all'
    # repos_commit   = 'REPOS commit all'
    # repos_push     = 'REPOS push all'
    backup         = 'BACKUP & RETRIEVE'


def args_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--which", help="which option to run", type=str, default=None)  # , choices=[op.value for op in Options]
    args = parser.parse_args()
    main(which=args.which)


def main(which=None):
    PROGRAM_PATH.delete(sure=True, verbose=False)
    options = [op.value for op in Options]
    if which is None: choice_key = display_options(msg="", options=options, header="DEVOPS", default=options[0])
    else: choice_key = Options[which].value

    if choice_key == Options.update.value:
        import machineconfig.scripts.python.devops_update_repos as helper
        program = helper.main()

    elif choice_key == Options.ve.value:
        from machineconfig.jobs.python.python_ve_installer import main
        program = main()

    elif choice_key == Options.devaps.value:
        from machineconfig.scripts.python.devops_devapps_install import main
        program = main()

    elif choice_key == Options.sym_new.value:
        from machineconfig.jobs.python.python_ve_symlink import main
        program = main()

    elif choice_key == Options.sym_path_shell.value:
        from machineconfig.profile.create import main
        main()
        program = "echo 'done with symlinks'"

    elif choice_key == Options.ssh_add_pubkey.value:
        from machineconfig.scripts.python.devops_add_ssh_key import main
        program = main()

    elif choice_key == Options.ssh_use_pair.value:
        raise NotImplementedError

    elif choice_key == Options.ssh_add_id.value:  # so that you can SSH directly withuot pointing to identity key.
        from machineconfig.scripts.python.devops_add_identity import main
        program = main()

    elif choice_key == Options.ssh_setup.value:
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == Options.ssh_setup_wsl.value:
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == Options.backup.value:
        from machineconfig.scripts.python.devops_backup_retrieve import main
        program = main()

    else: raise ValueError(f"Unimplemented choice: {choice_key}")
    if program: write_shell_script(program, display=True, preserve_cwd=True, desc="Shell script prepared by Python.", execute=True if which is not None else False)
    else: write_shell_script("echo 'Done.'", display=False, )  # Python did not return any script to run.


if __name__ == "__main__":
    args_parser()
