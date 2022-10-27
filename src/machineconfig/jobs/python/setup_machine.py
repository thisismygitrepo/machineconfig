
"""This module provides convenience functions to setup a remote machine,
irrespective of whether the local is Windows or Linux, the remote is Windows or Linux.
"""

import clipboard
import crocodile.toolbox as tb
# from machineconfig import create_symlinks


# those functions assume an activated virtual enviroment in shell.
def ssh_keys_setup(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/openssh-server_add-sshkey.{'ps1' if system == 'Windows' else 'sh'}").read_text()

# unused functions:
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])


def setup():
    # step one is install openshh-server on remote machine, see [setup_windows/setup_linux]/openssh-server.[ps1/.sh]
    ssh = tb.SSH(username="username", hostname="hostname", pwd=None, env=(ve := "ve"))  # use pwd for the first time connection.
    system = ssh.remote_machine
    ssh.open_console(terminal="wt")  # keep this window for emergency.

    ssh.copy_from_here("~/.ssh/id_rsa.pub")
    ssh.print_summary()
    ssh.copy_from_here("~/dotfiles", zip_first=True)
    ssh.print_summary()

    # OR: if it is local setup:
    # cd ~/code/machineconfig/src/machineconfig
    # python -m fire ./jobs/backup_retrieve.py retrieve_dotfiles  # assuming key.zip is in Downloads folder.
    if system == "Windows": ssh.run("~/machineconfig/src/machineconfig/setup_windows/devapps.ps1")
    ssh_script = ssh_keys_setup(system=system)


if __name__ == '__main__':
    pass
