
import crocodile.toolbox as tb
from machineconfig import create_symlinks


def setup_env(system, env_name="ve", py_version="310"):
    scripts = tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/setup_ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    scripts = scripts.replace("ve_name='ve'", f"ve_name='{env_name}'")
    if system == "Windows": scripts = scripts.replace("py_version=39", f"py_version='{py_version}'")
    elif system == "Linux": scripts = scripts.replace("py_version=3.9", f"py_version='{py_version.replace('.', '')}'")
    else: raise ValueError
    return scripts


# those functions assume an activated virtual enviroment in shell.
def get_repos_install_script(system): return tb.P.cwd().parent.joinpath(f"setup_{system.lower()}/setup_repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])


def setup_locally():
    env = "ve10"
    ssh = tb.Terminal()
    from crocodile.environment import system
    ssh.run(setup_env(system, env_name=env, py_version="310"))
    env_cmd = f"""& ("~/venvs/" + {env} + "/Scripts/Activate.ps1")""" if system == 'Windows' else f"""source ~/venvs/{env}/bin/activate"""
    ssh.run(env_cmd + "; " + get_repos_install_script(system))
    create_symlinks.main()


def setup_remotely():
    ve = "ve10"
    ssh = tb.SSH(username="alex", hostname="localhost", env=ve)
    system = ssh.remote_machine
    ssh.run(setup_env(system=system, env_name=ve, py_version="310"))
    ssh.run(ssh.remote_env_cmd + "; " + get_repos_install_script(system))
    ssh.run(ssh.remote_env_cmd + "; " + "python -m fire machineconfig.create_symlink main")


if __name__ == '__main__':
    pass
