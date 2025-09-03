"""
Utils
"""

from machineconfig.utils.path_reduced import P as PathExtended
import machineconfig
from machineconfig.utils.options import check_tool_exists, choose_cloud_interactively, choose_multiple_options, choose_one_option, choose_ssh_host, display_options
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.links import build_links, symlink_copy, symlink_func
from machineconfig.utils.code import get_shell_script_executing_python_file, get_shell_file_executing_python_script, write_shell_script_to_default_program_path, print_code, PROGRAM_PATH
from machineconfig.utils.path import sanitize_path, match_file_name

# Split into multiple assignments to fix incompatible tuple sizes
_ = get_shell_script_executing_python_file, get_shell_file_executing_python_script, print_code, PROGRAM_PATH, display_options, write_shell_script_to_default_program_path
_ = build_links
_ = symlink_copy
_ = symlink_func
_ = check_tool_exists
_ = choose_cloud_interactively
_ = choose_multiple_options
_ = choose_one_option
_ = choose_ssh_host
_ = sanitize_path
_ = match_file_name


LIBRARY_ROOT = PathExtended(machineconfig.__file__).resolve().parent  # .replace(str(PathExtended.home()).lower(), PathExtended.home().str)
REPO_ROOT = LIBRARY_ROOT.parent.parent
CONFIG_PATH = PathExtended.home().joinpath(".config/machineconfig")
INSTALL_VERSION_ROOT = CONFIG_PATH.joinpath("cli_tools_installers/versions")
INSTALL_TMP_DIR = PathExtended.home().joinpath("tmp_results", "tmp_installers")
DEFAULTS_PATH = PathExtended.home().joinpath("dotfiles/machineconfig/defaults.ini")


# def get_latest_version(url: str) -> None:
#     # not yet used, consider, using it.
#     import requests
#     import json
#     url = f"https://api.github.com/repos/{url.split('github.com/')[1]}/releases/latest"
#     # Replace {owner} and {repo} with the actual owner and repository name
#     response = requests.get(url, timeout=10)
#     if response.status_code == 200:
#         data = json.loads(response.text)
#         latest_version = data["tag_name"]
#         print(f"\n📦 VERSION INFO | Latest release: {latest_version}\n")
#     else: print(f"\n❌ ERROR | API request failed: {response.status_code}\n")




def check_dotfiles_version_is_beyond(commit_dtm: str, update: bool) -> bool:
    dotfiles_path = str(PathExtended.home().joinpath("dotfiles"))
    from git import Repo
    repo = Repo(path=dotfiles_path)
    last_commit = repo.head.commit
    dtm = last_commit.committed_datetime
    from datetime import datetime  # make it tz unaware
    dtm = datetime(dtm.year, dtm.month, dtm.day, dtm.hour, dtm.minute, dtm.second)
    res =  dtm > datetime.fromisoformat(commit_dtm)
    if res is False and update is True:
        console = Console()
        console.print(Panel(f"🔄 UPDATE REQUIRED | Updating dotfiles because {dtm} < {datetime.fromisoformat(commit_dtm)}", border_style="bold blue", expand=False))
        from machineconfig.scripts.python.cloud_repo_sync import main
        main(cloud=None, path=dotfiles_path)
    return res

def wait_for_jobs_to_finish(root: PathExtended, pattern: str, wait_for_n_jobs: int, max_wait_minutes: float) -> bool:
    wait_finished: bool=False
    import time
    t0 = time.time()
    while not wait_finished:
        parts = root.search(pattern, folders=False, r=False)
        counter  =  len(parts)
        if counter == wait_for_n_jobs:
            wait_finished = True
            console = Console()
            console.print(Panel(f"✅ JOB COMPLETE | {counter} Jobs finished successfully. Exiting.", border_style="bold blue", expand=False))
            return True
        if (time.time() - t0) > 60 * max_wait_minutes:
            console = Console()
            console.print(Panel(f"⏱️  TIMEOUT | Waited for {max_wait_minutes} minutes. Exiting.", border_style="bold blue", expand=False))
            return False
        print(f"""
⏳ PROGRESS | {counter}/{wait_for_n_jobs} jobs finished. Waiting for {wait_for_n_jobs - counter} more jobs to complete, sleeping for 60 seconds.
""")
        time.sleep(60)
    return False



if __name__ == '__main__':
    # import typer
    # typer.run(check_tool_exists)
    pass
