"""checkout_version.py
"""

from crocodile.file_management import P, Save, randstr
from crocodile.meta import Terminal
from machineconfig.utils.ve_utils.ve1 import get_ve_specs
from machineconfig.scripts.python.repos import record_a_repo, install_repos
import platform

from machineconfig.utils.ve_utils.ve1 import get_ve_name_and_ipython_profile


def checkout_version(version: str, repo_root: P, exclude_editable: bool=False):
    """Checkout a version of the repo and install its requirements."""
    ve_name, _ipyprofile = get_ve_name_and_ipython_profile(init_path=repo_root)
    if ve_name is None: raise ValueError("❌ No virtual environment found.")
    ve_path = P.home().joinpath("venvs", ve_name or "ve")
    ve_specs = get_ve_specs(ve_path)
    try:
        py_version = ve_specs['version']
    except KeyError as err:
        # print(f"❌ No python version found in {ve_specs}.")
        # raise err
        _ = err
        py_version = ve_specs['version_info']
    sys = platform.system().lower()

    target_dir = repo_root.expanduser().absolute().joinpath(f"versions/{version}").as_posix()
    if exclude_editable:
        editable_json = get_editable_packages(ve_name=ve_name)
        specs_path = P(target_dir).expanduser().joinpath("editable_packages.json")
        Save.json(obj=editable_json, path=specs_path, indent=4)
        install_editable_packages = install_repos(specs_path=str(specs_path), editable_install=True)
    else: install_editable_packages = ""

    version_root = repo_root.collapseuser().joinpath(f"versions/{version}").as_posix()
    version_root_obj = P(version_root).expanduser().create()
    checkout_ve = f"{repo_root.name}-{version}-prod" if not exclude_editable else ve_name
    checkout_ve = input(f"📝 Name of the ve to create (default: {checkout_ve}): ") or checkout_ve

    install_env = f"""

uv venv $HOME/venvs/{checkout_ve} --python {py_version} --python-preference only-managed
. $HOME/scripts/activate_ve {ve_name}

uv pip install pip

{install_editable_packages}

cd {version_root}
uv pip install -r requirements_{sys}.txt

"""
    if sys == "windows":
        version_root_obj.joinpath("install_env.ps1").write_text(install_env)
        if not version_root_obj.joinpath("install_env.sh").exists():
            version_root_obj.joinpath("install_env.sh").write_text(install_env)
    elif sys == "linux":
        version_root_obj.joinpath("install_env.sh").write_text(install_env)
        if not version_root_obj.joinpath("install_env.ps1").exists():
            version_root_obj.joinpath("install_env.ps1").write_text(install_env)
    else:
        raise NotImplementedError(f"🚫 System {sys} not supported.")

    pip_freeze_script = f"""
cd '{target_dir}'
. "$HOME/scripts/activate_ve" {ve_name}
python -m pip freeze {'--exclude-editable' if exclude_editable else ''} > requirements_{sys}.txt
"""
    Terminal().run_script(pip_freeze_script, verbose=True, shell="default").print()
    print(f"""
{'=' * 70}
✅ SUCCESS | Requirements for version {version} installed successfully
{'=' * 70}
""")


def main():
    from git.repo import Repo
    from git.exc import InvalidGitRepositoryError
    try:
        repo = Repo(P.cwd(), search_parent_directories=True)
        print(f"""
{'=' * 70}
🔍 GIT REPO | Found repository at {repo.working_dir}
{'=' * 70}
""")
    except InvalidGitRepositoryError as err:
        print(f"""
{'🔥' * 20}
❌ ERROR | No Git repository found at {P.cwd()} or its parent directories
{'🔥' * 20}
""")
        raise err
    version = input("📝 Enter version name: ")
    from rich.prompt import Confirm
    exclude_editable = Confirm.ask("🔄 Exclude editable packages?", default=False)

    repo_root = P(repo.working_dir)
    checkout_version(version, repo_root, exclude_editable=exclude_editable)


def get_editable_packages(ve_name: str):
    file = P.tmp().joinpath(f"tmp_files/editable_requirements_{randstr()}.txt")
    file.parent.mkdir(parents=True, exist_ok=True)
    editable_packages_script = f"""
. $HOME/scripts/activate_ve {ve_name}
pip list --editable > {file}
"""
    Terminal().run_script(editable_packages_script, verbose=True, shell="default").print()
    try: tmp3 = file.read_text(encoding='utf-16').splitlines()[2:]
    except UnicodeError: tmp3 = file.read_text().splitlines()[2:]

    res = []
    for a_pkg in tmp3:
        tmp = P(a_pkg.split(" ")[-1].rstrip())
        tmp1 = record_a_repo(tmp, search_parent_directories=True)  # pip list --editable returns path to package or repo in a way not yet understood.
        res.append(tmp1)
    return res


if __name__ == "__main__":
    pass
