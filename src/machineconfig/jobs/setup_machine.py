
"""This module provides convenience functions to setup a remote machine,
irrespective of whether the local is Windows or Linux, the remote is Windows or Linux.
"""

import clipboard
import crocodile.toolbox as tb
# from machineconfig import create_symlinks


def apps_setup(system):
    script = tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/apps_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    return script
def ve_setup(system, env_name="ve", dotted_py_version="3.10"):
    scripts = tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/ve_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    scripts = tb.modify_text(raw=scripts, txt="ve_name=", alt=f"ve_name='{env_name}'", newline=True)
    scripts = tb.modify_text(raw=scripts, txt="py_version=", alt=f"py_version='{dotted_py_version.replace('.', '') if system == 'Windows' else dotted_py_version}'", newline=True)
    return scripts

# those functions assume an activated virtual enviroment in shell.
def repos_setup(system, ve): return tb.modify_text(raw=tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/repos_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text(), txt="ve_name = ", alt=f"ve_name = '{ve}'", newline=True)
def symlinks_setup(system, ve): return tb.modify_text(raw=tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/semlinks_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text(), txt="ve_name = ", alt=f"ve_name = '{ve}'", newline=True)
def ssh_keys_setup(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/openssh_server_add_sshkey.{'ps1' if system == 'Windows' else 'sh'}").read_text()

# unused functions:
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])


def setup():
    # step one is install openshh-server on remote machine, see [setup_windows/setup_linux]/openssh_server_installation.[ps1/.sh]
    ssh = tb.SSH(username="username", hostname="hostname", pwd=None, env=(ve := "ve"))  # use pwd for the first time connection.

    system = ssh.remote_machine
    ssh.open_console(terminal="wt")  # keep this window for emergency.
    apps_script = apps_setup(system=system)
    ve_script = ve_setup(system=system, env_name=ve, dotted_py_version="3.9")
    repo_script = repos_setup(system=system, ve=ve)

    clipboard.copy(apps_script + "\n" + ve_script + "\n" + repo_script)

    assert ssh.run_py("tb.P.home()"), "Install repos first before proceeding."

    ssh.copy_from_here("~/.ssh/id_rsa.pub")
    ssh.copy_from_here("~/dotfiles", zip_first=True)
    # OR: if it is local setup:
    # cd ~/code/machineconfig/src/machineconfig
    # python -m fire ./jobs/backup_retrieve.py retrieve_dotfiles  # assuming key.zip is in Downloads folder.
    symlinks_script = symlinks_setup(system=system, ve=ve)
    ssh_script = ssh_keys_setup(system=system)

    clipboard.copy(symlinks_script + "\n" + ssh_script)


if __name__ == '__main__':
    pass
