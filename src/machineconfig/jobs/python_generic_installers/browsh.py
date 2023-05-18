

from machineconfig.utils.utils import get_latest_release, find_move_delete_linux, find_move_delete_windows
# import crocodile.toolbox as tb
import platform


__doc__ = """cpufetch is a small yet fancy CPU architecture fetching tool, like neofetch but for CPUs."""

def main(version=None):
    url = get_latest_release("https://github.com/browsh-org/browsh", version=version)
    if platform.system() == "Linux":
        download = url.joinpath(f"browsh_{str(url[-1]).replace('v', '')}_linux_amd64").download().with_name("cpufetch", inplace=True, overwrite=True)
        find_move_delete_linux(downloaded=download, tool_name="cpufetch")
    elif platform.system() == "Windows":
        url = url.joinpath(f"browsh_{str(url[-1]).replace('v', '')}_windows_amd64.exe")
        print(f"Downloading {url}")
        downloaded = url.download().with_name("browsh.exe", overwrite=True, inplace=True)
        find_move_delete_windows(downloaded=downloaded, tool_name="browsh.exe")
    else:
        raise Exception(f"Not supported OS for gitui {platform.system()}")


if __name__ == '__main__':
    main()
