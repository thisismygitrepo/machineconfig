
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/dandavison/delta")


def main():
    if system() == 'Windows':
        # from crocodile.environment import AppData
        # target = AppData
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(repo_url.as_url_str(), suffix=suffix, download_n_extract=True, delete=True, strip_v=True)
    else:
        release = get_latest_release(repo_url.as_url_str())
        path = release.joinpath(f"delta-{str(release[-1]).replace('v', '')}-x86_64-unknown-linux-gnu.tar.gz").download()
        downloaded = path.ungz_untar(inplace=True)
        _ = find_move_delete_linux(downloaded, "delta", delete=True)


if __name__ == '__main__':
    main()
    # pass
