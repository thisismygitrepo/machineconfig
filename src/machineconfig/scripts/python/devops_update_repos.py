
from platform import system
import crocodile.toolbox as tb
from machineconfig.utils.utils import write_shell_script


sep = "\n"


def main(verbose=True) -> str:
    _ = verbose
    repos = tb.P.home().joinpath("dotfiles/config/reposXXX.ini")
    if repos.exists():
        repos = repos.readit()
        repo_package_list = repos.sections()
    else:
        repos = ["~/code/crocodile", "~/code/machineconfig", ]
        repo_package_list = repos
    repos_objs = []
    for a_package_path in repo_package_list:
        try:
            repo = tb.install_n_import("git", "gitpython").Repo(str(tb.P(a_package_path).expanduser()), search_parent_directories=True)
            repos_objs.append(repo)
        except Exception as ex:
            print(ex)
    if system() == "Linux":
        additions = []
        for a_repo in repos_objs:
            if "machineconfig" in a_repo.working_dir:  # special treatment because of executables.
                an_addition = f"""
echo ""
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
cd "{a_repo.working_dir}"
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
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
cd "{a_repo.working_dir}"
{sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}
""")
        program = "\n".join(additions)

    elif system() == "Windows":
        program = "\n".join([f"""
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
cd "{a_repo.working_dir}"
{sep.join([f'git pull {remote.name}' for remote in a_repo.remotes])}
""" for a_repo in repos_objs])
    else: raise NotImplementedError(f"System {system()} not supported")
    write_shell_script(program, desc="Script to update repos")
    return ""


if __name__ == '__main__':
    pass
