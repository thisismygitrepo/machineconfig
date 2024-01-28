
"""Update
"""

from crocodile.file_management import P, Read
from crocodile.core import install_n_import
from machineconfig.utils.utils import DEFAULTS_PATH
from platform import system


sep = "\n"


def main(verbose: bool = True) -> str:
    _ = verbose
    repos: list[str] = ["~/code/crocodile", "~/code/machineconfig", ]
    try:
        tmp = Read.ini(DEFAULTS_PATH)['general']['repos'].split(",")
        if tmp[-1] == "": tmp = tmp[:-1]
        repos += tmp
    except (FileNotFoundError, KeyError, IndexError):
        print(f"Missing {DEFAULTS_PATH} or section [general] or key repos. Using default repos.")
        print(f"""It should look like this:
[general]
repos = ~/code/repo1,~/code/repo2
rclone_config_name = onedriveWork
email_config_name = Yahoo3
to_email = myemail@email.com
""")

    repos_objs = []
    for a_package_path in repos:
        try:
            repo = install_n_import("git", "gitpython").Repo(str(P(a_package_path).expanduser()), search_parent_directories=True)
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
# git reset --hard
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
