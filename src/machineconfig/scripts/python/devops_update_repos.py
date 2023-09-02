
"""Update
"""

from platform import system
import crocodile.toolbox as tb
# from machineconfig.utils.utils import write_shell_script

sep = "\n"


def main(verbose: bool = True) -> str:
    _ = verbose
    repos_file = tb.P.home().joinpath("dotfiles/machineconfig/setup/repos")

    repos: list[str] = ["~/code/crocodile", "~/code/machineconfig", ]
    if repos_file.exists():
        repos += [item.rstrip() for item in repos_file.read_text().split(",")]

    repos_objs = []
    for a_package_path in repos:
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
{sep.join([f'git pull {remote.name} {a_repo.active_branch.name}' for remote in a_repo.remotes])}
""")
        program = "\n".join(additions)

    elif system() == "Windows":
        program = "\n".join([f"""
echo "{("Pulling " + str(a_repo.working_dir)).center(80, "-")}"
cd "{a_repo.working_dir}"
{sep.join([f'git pull {remote.name} {a_repo.active_branch.name}' for remote in a_repo.remotes])}
""" for a_repo in repos_objs])
    else: raise NotImplementedError(f"System {system()} not supported")
    # write_shell_script(program, desc="Script to update repos")
    # return ""
    return program


# def get_pulls(remote):
#     if len(remote.branches) == 0: return ""
#     elif len(remote.branches) == 1: return f'git pull {remote.name} {remote.branches[0].name}'
#     else: return f'git pull {remote.name} {remote.active_branch.name}'


if __name__ == '__main__':
    pass
