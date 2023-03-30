
from platform import system
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT
from rich.panel import Panel
from rich.console import Console
# from rich.text import Text
from rich.syntax import Syntax


def main(verbose=True) -> str:
    repos = tb.P.home().joinpath("dotfiles/config/reposXXX.ini")
    if repos.exists():
        repos = repos.readit()
        repo_package_list = repos.sections()
    else:
        repos = {
            "crocodile": dict(name="crocodile", url="http://github.com/thisismygitrepo/crocodile", py_package="True", path=""),
            "machineconfig": dict(name="machineconfig", url="http://github.com/thisismygitrepo/machineconfig", py_package="True", path="")
                }
        repo_package_list = repos.keys()

    local_install_repos = []
    global_packages = []
    for a_package in repo_package_list:
        try:
            a_package_path = tb.P(__import__(a_package).__file__) if repos[a_package]["py_package"] == "True" else tb.P(repos[a_package]["path"]).expanduser().absolute()
            if not a_package_path.exists():
                if verbose: print(f"Couldn't find {a_package} repo. Cloning from remote {repos[a_package]['url']} to ~/code/{a_package} ...")
                tb.Terminal().run(f"cd ~/code; git clone {repos[a_package]['url']}")
            repo = tb.install_n_import("git", "gitpython").Repo(str(a_package_path), search_parent_directories=True)
            local_install_repos.append(repo)
        except:
            if repos[a_package]["py_package"] == "False":
                continue
            global_packages.append(a_package)

    if verbose: print(f"Local install repos:"); tb.L(local_install_repos).print(); print("Global packages:"); tb.L(global_packages).print()
    sep = "\n"
    if system() == "Linux":
        program = tb.P(f"{LIBRARY_ROOT}/jobs/linux/update_essentials").read_text()
        additions = []
        for a_repo in local_install_repos:
            if "machineconfig" in a_repo.working_dir:  # special treatment because of executables.
                an_addition = f"""
cd "{a_repo.working_dir}"
echo ""
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
git reset --hard
git pull origin
chmod +x ~/scripts -R
chmod +x ~/code/machineconfig/src/machineconfig/jobs/linux -R
chmod +x ~/code/machineconfig/src/machineconfig/settings/lf/linux/exe -R
"""
                additions.append(an_addition)
            else:
                # if a_repo.is_dirty() and input(f"Repository {a_repo} is not clean, hard-reset it? y/[n]"): a_repo.git.reset('--hard')
                additions.append(f"""
cd "{a_repo.working_dir}"
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
{sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}
""")
        addition = "\n".join(additions)

    elif system() == "Windows":
        program = tb.P(f"{LIBRARY_ROOT}/jobs/windows/update_essentials.ps1").read_text()
        addition = "\n".join([f"""
cd "{a_repo.working_dir}"
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
{sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}
""" for a_repo in local_install_repos])
    else: raise NotImplementedError(f"System {system()} not supported")

    program = program.split("# updateBegins")[0] + addition + program.split("# updateEnds")[1]
#    program += f"\npip install --upgrade {' '.join(global_packages)}\n" if len(global_packages) else ""
    console = Console()
    console.print(Panel(Syntax(program, lexer="ps1" if system == "Windows" else "sh"), title="Script to create virtual environment..."), style="bold red")
    return program


if __name__ == '__main__':
    pass
