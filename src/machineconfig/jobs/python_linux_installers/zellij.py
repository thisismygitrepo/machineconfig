from machineconfig.utils.installer import find_move_delete_linux, get_latest_release
import crocodile.toolbox as tb
from typing import Optional

# bash_integration = """
#
# # adopted from https://zellij.dev/documentation/integration.html
# # eval "$(zellij setup --generate-auto-start bash)"
# z_ls  # make sure it is towards the end of the script.
#
# """  # MOVED TO PATCHES


__doc__ = """Zellij is a terminal workspace with support for multiple plugins, such as a terminal, status bar, tabs, splits, etc."""
repo_url = "https://github.com/zellij-org/zellij"


def main(version: Optional[str] = None):
    _ = version
    _ = get_latest_release(repo_url=repo_url, exe_name="zellij", download_n_extract=False)
    download = tb.P(f"https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded=download, tool_name="zellij")

    # profile_path = tb.P.home().joinpath(".bashrc")
    # profile_text = profile_path.read_text()
    # if bash_integration not in profile_text:
    #     profile_path.write_text(profile_text + bash_integration)


if __name__ == '__main__':
    main()
