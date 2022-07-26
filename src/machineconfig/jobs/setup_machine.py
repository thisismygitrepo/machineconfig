
"""This module provides convenience functions to setup a remote machine,
irrespective of whether the local is Windows or Linux, the remote is Windows or Linux.
"""

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
def get_repos_install_script(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/repos_setup.{'ps1' if system == 'Windows' else 'sh'}").read_text()
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])
def add_ssh_keys(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/openssh_server_add_sshkey.ps1").read_text()


def setup_locally():
    env = "ve10"
    ssh = tb.Terminal()
    from crocodile.environment import system
    ssh.run(ve_setup(system, env_name=env, dotted_py_version="3.10"))
    env_cmd = f"""& ("~/venvs/" + {env} + "/Scripts/Activate.ps1")""" if system == 'Windows' else f"""source ~/venvs/{env}/bin/activate"""
    ssh.run(env_cmd + "; " + get_repos_install_script(system))
    create_symlinks.main()


def setup_remotely():
    # step one is install openshh-server on remote machine, see [setup_windows/setup_linux]/openssh_server_installation.[ps1/.sh]
    ssh = tb.SSH(username="username", hostname="hostname", pwd=None, env=(ve := "ve"))  # use pwd for the first time connection.
    ssh.run(apps_setup(system=ssh.remote_machine))
    ssh.run(ve_setup(system=ssh.remote_machine, env_name=ve, dotted_py_version="3.9"))
    ssh.run(ssh.remote_env_cmd + "\n" + get_repos_install_script(system=ssh.remote_machine))
    ssh.copy_from_here("~/.ssh/id_rsa.pub")
    ssh.run(add_ssh_keys(system=ssh.remote_machine))
    ssh.run(ssh.remote_env_cmd + "\n" + "python -m fire machineconfig.create_symlinks main")


if __name__ == '__main__':
    pass
