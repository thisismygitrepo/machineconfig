"""Update repositories with fancy output
"""

from crocodile.file_management import P, Read
from machineconfig.utils.utils import DEFAULTS_PATH
from platform import system


sep = "\n"


def main(verbose: bool=True) -> str:
    _ = verbose
    repos: list[str] = ["~/code/crocodile", "~/code/machineconfig", ]
    try:
        tmp = Read.ini(DEFAULTS_PATH)['general']['repos'].split(",")
        if tmp[-1] == "": tmp = tmp[:-1]
        repos += tmp
    except (FileNotFoundError, KeyError, IndexError):
        print(f"🚫 Missing {DEFAULTS_PATH} or section [general] or key repos. Using default repos.")
        print("""✨ It should look like this:
[general]
repos = ~/code/repo1,~/code/repo2
rclone_config_name = onedrivePersonal
email_config_name = Yahoo3
to_email = myemail@email.com
""")

    repos_objs = []
    for a_package_path in repos:
        try:
            import git
            repo = git.Repo(str(P(a_package_path).expanduser()), search_parent_directories=True)
            repos_objs.append(repo)
        except Exception as ex:
            print(f"❌ Error: {ex}")

    if system() == "Linux":
        additions = []
        for a_repo in repos_objs:
            if "machineconfig" in a_repo.working_dir:  # special treatment because of executables.
                an_addition = f"""
echo ""
echo "🔄 {("Updating " + str(a_repo.working_dir)).center(80, "═")}"
echo "🛠  Special handling for machineconfig repository..."
cd "{a_repo.working_dir}"
# git reset --hard
git pull origin &
chmod +x ~/scripts -R
chmod +x ~/code/machineconfig/src/machineconfig/jobs/linux -R
chmod +x ~/code/machineconfig/src/machineconfig/settings/lf/linux/exe -R
"""
                additions.append(an_addition)
            else:
                additions.append(f"""
echo "🔄 {("Updating " + str(a_repo.working_dir)).center(80, "═")}"
cd "{a_repo.working_dir}"
{sep.join([f'git pull {remote.name} {a_repo.active_branch.name} &' for remote in a_repo.remotes])}
"""
)
        program = "\n".join(additions)

    elif system() == "Windows":
        program = "\n".join([f"""
echo "🔄 {("Updating " + str(a_repo.working_dir)).center(80, "═")}"
cd "{a_repo.working_dir}"
{sep.join([f'git pull {remote.name} {a_repo.active_branch.name} &' for remote in a_repo.remotes])}
""" for a_repo in repos_objs])
    else: raise NotImplementedError(f"⚠️ System {system()} not supported")
    return program


if __name__ == '__main__':
    pass
