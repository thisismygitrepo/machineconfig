
""" Chatgpt installer   """

# from crocodile.meta import sys
from machineconfig.utils.installer import find_move_delete_windows, find_move_delete_linux, get_latest_release
from platform import system
from typing import Optional
import crocodile.toolbox as tb


repo_url = "https://github.com/j178/chatgpt"
# see also: https://github.com/marcolardera/chatgpt-cli & https://github.com/kharvd/gpt-cli


def main(version: Optional[str] = None) -> None:
    _ = version
    latest = get_latest_release(repo_url=repo_url, exe_name="chatgpt", download_n_extract=False)
    if not isinstance(latest, tb.P):
        print(f"Could not find browsh release for version {version}")
        return None
    if system() == "Windows":
        downloaded = latest.joinpath("chatgpt_Windows_x86_64.zip").download().unzip(inplace=True)
        find_move_delete_windows(downloaded_file_path=downloaded)
    elif system() == "Linux":
        downloaded = latest.joinpath("chatgpt_Linux_x86_64.tar.gz").download().ungz_untar(inplace=True)
        find_move_delete_linux(downloaded=downloaded, tool_name="chatgpt")


if __name__ == "__main__":
    main()
