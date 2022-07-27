
"""This module provides convenience functions to setup a remote machine,
irrespective of whether the local is Windows or Linux, the remote is Windows or Linux.
"""
import clipboard
import crocodile.toolbox as tb
from machineconfig import create_symlinks


def apps_setup(system):
    script = tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/apps_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    return script
def ve_setup(system, env_name="ve", dotted_py_version="310"):
    scripts = tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/ve_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    scripts = scripts.replace("ve_name='ve'", f"ve_name='{env_name}'")
    if system == "Windows": scripts = scripts.replace("py_version=39", f"py_version='{dotted_py_version.replace('.', '')}'")
    elif system == "Linux": scripts = scripts.replace("py_version=3.9", f"py_version='{dotted_py_version}'")
    else: raise ValueError
    return scripts
# those functions assume an activated virtual enviroment in shell.
def get_repos_install_script(system, ve): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/repos_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text().replace("ve_name = 've'", f"ve_name = '{ve}'")
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])
def add_ssh_keys(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/openssh_server_add_sshkey.{'ps1' if system == 'Windows' else 'sh'}").read_text()


def setup():
    # step one is install openshh-server on remote machine, see [setup_windows/setup_linux]/openssh_server_installation.[ps1/.sh]
    ssh = tb.SSH(username="username", hostname="hostname", pwd=None, env=(ve := "ve"))  # use pwd for the first time connection.
    system = ssh.remote_machine
    ssh.open_console(terminal="wt")  # keep this window for emergency.
    clipboard.copy(apps_setup(system=system))
    clipboard.copy(ve_setup(system=system, env_name=ve, dotted_py_version="3.9"))
    clipboard.copy(get_repos_install_script(system=system, ve=ve))

    ssh.copy_from_here("~/.ssh/id_rsa.pub")
    # be careful, if you intend to copy dotfiles to remote machine, you need to re-run the command below:
    clipboard.copy(add_ssh_keys(system=system))
    clipboard.copy(ssh.remote_env_cmd + "\n" + "python -m fire machineconfig.create_symlinks main")


if __name__ == '__main__':
    pass
