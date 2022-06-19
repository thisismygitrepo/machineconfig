
import crocodile.toolbox as tb


def setup_ve(ve_name="ve", py_version="310"):
    scripts = tb.P.cwd().parent.joinpath("windows_setup/setup_ve.ps1").read_text()
    scripts = scripts.replace("$ve_name = 've'", f"$ve_name = '{ve_name}'")
    scripts = scripts.replace("$py_version = 39", f"$py_version = '{py_version}'")
    return scripts


def install_requirements(*repos):
    res = [f"cd ~/code/{repo}; pip install -r requirements.txt" for repo in repos]
    return "; ".join(res)


def main():
    ssh = tb.SSH(username="alex", hostname="localhost", ve="latest")
    # ssh = tb.Terminal()
    ssh.run(setup_ve(ve_name="latest", py_version="310"))
    ssh.run(ssh.local_python_cmd + "; " + install_requirements("crocodile"))


if __name__ == '__main__':
    pass
