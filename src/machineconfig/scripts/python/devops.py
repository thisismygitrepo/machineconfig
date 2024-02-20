


"""devops
"""
from crocodile.file_management import P
from machineconfig.utils.utils import display_options, PROGRAM_PATH, write_shell_script
from platform import system
from enum import Enum
from typing import Optional


class Options(Enum):
    update         = 'UPDATE essential repos'
    cli_install    = 'DEVAPPS install'
    ve             = 'VE install'
    sym_path_shell = 'SYMLINKS, PATH & SHELL PROFILE'
    sym_new        = 'SYMLINKS new'
    ssh_add_pubkey = 'SSH add pub key to this machine'
    ssh_add_id     = 'SSH add identity (private key) to this machine'
    ssh_use_pair   = 'SSH use key pair to connect two machines'
    ssh_setup      = 'SSH setup'
    ssh_setup_wsl  = 'SSH setup wsl'
    backup         = 'BACKUP'
    retreive       = 'RETRIEVE'
    scheduler      = 'SCHEDULER'


def args_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--which", help="which option to run", type=str, default=None)  # , choices=[op.value for op in Options]
    args = parser.parse_args()
    main(which=args.which)


def main(which: Optional[str] = None):
    PROGRAM_PATH.delete(sure=True, verbose=False)
    options = [op.value for op in Options]
    if which is None:
        # import questionary
        # choice_key = questionary.autocomplete(message="Which option to run?", choices=options, default=options[0]).ask()
        choice_key = display_options(msg="", options=options, header="DEVOPS", default=options[0])
    else: choice_key = Options[which].value

    if choice_key == Options.update.value:
        import machineconfig.scripts.python.devops_update_repos as helper
        program = helper.main()

    elif choice_key == Options.ve.value:
        program = ""
        reply: bool = False
        if P.cwd().joinpath(".ve.ini").exists():
            reply = input("Detected .ve.ini file. Do you want to use it to build ve? (y/[n]): ") == "y"
            if reply:
                from machineconfig.utils.ve import get_ve_install_script_from_specs
                program_win = get_ve_install_script_from_specs(repo_root=P.cwd().str, system="Windows")
                program_lin = get_ve_install_script_from_specs(repo_root=P.cwd().str, system="Linux")
                install_reply = input("Proceed with installation? (y/[n]): ") == "y"
                if not install_reply: program = ""
                else:
                    if system() == "Windows": program = program_win
                    elif system() == "Linux": program = program_lin
                    else: raise ValueError(f"Unknown system: {system()}")

        if not reply:
            from machineconfig.utils.ve import get_ve_install_script
            program = get_ve_install_script()

    elif choice_key == Options.cli_install.value:
        import machineconfig.scripts.python.devops_devapps_install as helper
        program = helper.main()

    elif choice_key == Options.sym_new.value:
        import machineconfig.jobs.python.python_ve_symlink as helper
        program = helper.main()

    elif choice_key == Options.sym_path_shell.value:
        import machineconfig.profile.create as helper
        helper.main()
        program = "echo '✅ done with symlinks'"

    elif choice_key == Options.ssh_add_pubkey.value:
        import machineconfig.scripts.python.devops_add_ssh_key as helper
        program = helper.main()

    elif choice_key == Options.ssh_use_pair.value:
        raise NotImplementedError

    elif choice_key == Options.ssh_add_id.value:  # so that you can SSH directly withuot pointing to identity key.
        import machineconfig.scripts.python.devops_add_identity as helper
        program = helper.main()

    elif choice_key == Options.ssh_setup.value:
        program_windows = f"""Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh_all.ps1 | Invoke-Expression  # https://github.com/thisismygitrepo.keys"""
        program_linux = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_all.sh | sudo bash  # https://github.com/thisismygitrepo.keys"""
        program = program_linux if system() == "Linux" else program_windows

    elif choice_key == Options.ssh_setup_wsl.value:
        program = f"""curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/openssh_wsl.sh | sudo bash"""

    elif choice_key == Options.backup.value:
        from machineconfig.scripts.python.devops_backup_retrieve import main as helper
        program = helper(direction="BACKUP")
    elif choice_key == Options.retreive.value:
        from machineconfig.scripts.python.devops_backup_retrieve import main as helper
        program = helper(direction="RETRIEVE")

    elif choice_key == Options.scheduler.value:
        from machineconfig.scripts.python.scheduler import main as helper
        program = helper()

    else: raise ValueError(f"Unimplemented choice: {choice_key}")
    if program: write_shell_script(program, display=True, preserve_cwd=True, desc="Shell script prepared by Python.", execute=True if which is not None else False)
    else: write_shell_script("echo 'Done.'", display=False, )  # Python did not return any script to run.


if __name__ == "__main__":
    args_parser()
