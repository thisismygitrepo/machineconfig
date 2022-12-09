
from platform import system
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT


def main():
    repos = tb.P.home().joinpath("dotfiles/config/repos.ini")
    local_install_repos = []
    global_packages = []

    if repos.exists():
        repos = repos.readit()
        repo_package_list = list(repos.keys())
        repo_package_list.remove("DEFAULT")
    else: repo_package_list = ["crocodile", "machineconfig"]

    for a_package in repo_package_list:
        try:
            repo = tb.install_n_import("git", "gitpython").Repo(__import__(a_package).__file__, search_parent_directories=True)
            local_install_repos.append(repo)
        except:
            global_packages.append(a_package)

    sep = "\n"
    if system() == "Linux":
        program = tb.P(f"{LIBRARY_ROOT}/jobs/linux/update_essentials").read_text()
        additions = []
        for a_repo in local_install_repos:
            if "machineconfig" in a_repo.working_dir:
                an_addition = f"""
cd "{a_repo.working_dir}"
git reset --hard
git pull origin
chmod +x ~/scripts -R
chmod +x ~/code/machineconfig/src/machineconfig/jobs/linux -R
chmod +x ~/code/machineconfig/settings/lf_linux/exe -R
"""
                additions.append(an_addition)
            else:
                additions.append(f"""cd "{a_repo.working_dir}"; {sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}""")
        addition = "\n".join(additions)
    elif system() == "Windows":
        program = tb.P(f"{LIBRARY_ROOT}/jobs/windows/update_essentials.ps1").read_text()
        addition = "\n".join([f"""cd "{a_repo.working_dir}"; {sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}""" for a_repo in local_install_repos])
    else: raise NotImplementedError(f"System {system()} not supported")

    program = program.split("# updateBegins")[0] + addition + program.split("# updateEnds")[1]
    program += f"\npip install --upgrade {' '.join(global_packages)}\n" if len(global_packages) else ""
    return program


if __name__ == '__main__':
    pass
