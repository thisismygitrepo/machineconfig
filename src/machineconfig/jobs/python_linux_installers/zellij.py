

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
import crocodile.toolbox as tb

# bash_integration = """
#
# # adopted from https://zellij.dev/documentation/integration.html
# # eval "$(zellij setup --generate-auto-start bash)"
# z_ls  # make sure it is towards the end of the script.
#
# """  # MOVED TO PATCHES


__doc__ = """Zellij is a terminal workspace with support for multiple plugins, such as a terminal, status bar, tabs, splits, etc."""

def main(version=None):
    _ = version
    _ = get_latest_release("https://github.com/zellij-org/zellij", download_n_extract=False, linux=True)
    download = tb.P(f"https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz").download().ungz_untar(inplace=True)
    find_move_delete_linux(downloaded=download, tool_name="zellij")

    # profile_path = tb.P.home().joinpath(".bashrc")
    # profile_text = profile_path.read_text()
    # if bash_integration not in profile_text:
    #     profile_path.write_text(profile_text + bash_integration)


if __name__ == '__main__':
    main()

