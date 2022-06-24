
import crocodile.toolbox as tb


def setup_env(env_name="ve", py_version="310"):
    scripts = tb.P.cwd().parent.joinpath("windows_setup/setup_ve.ps1").read_text()
    scripts = scripts.replace("$ve_name = 've'", f"$ve_name = '{env_name}'")
    scripts = scripts.replace("$py_version = 39", f"$py_version = '{py_version}'")
    return scripts


# those functions assume an activated virtual enviroment in shell.
def clone_repos(*repos): return "; ".join([f'cd ~/code; git clone {repo} --depth 4' for repo in repos])
def install_repos_requirements(*repos): return "; ".join([f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos])
def install_repos_locally(*repos): return "; ".join([f'cd ~/code/{repo}; pip install -e .' for repo in repos])


def main():
    ssh = tb.SSH(username="alex", hostname="localhost", ve="latest")
    # ssh = tb.Terminal()
    ssh.run(setup_ve(ve_name="latest", py_version="310"))

    ssh.run(ssh.local_python_cmd + "; " + clone_repos("crocodile"))
    ssh.run(ssh.local_python_cmd + "; " + clone_repos("machineconfig"))


if __name__ == '__main__':
    pass
