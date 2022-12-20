
from machineconfig.utils.utils import get_latest_release, find_move_delete_linux
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/dandavison/delta")
# from https://github.com/dandavison/delta#configuration
config_patch = """
[core]
    pager = delta

[interactive]
    diffFilter = delta --color-only

[delta]
    navigate = true    # use n and N to move between diff sections
    light = false      # set to true if you're in a terminal w/ a light background color (e.g. the default macOS terminal)

[merge]
    conflictstyle = diff3

[diff]
    colorMoved = default
"""

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

    config_path = tb.P.home().joinpath(".gitconfig")
    if config_path.exists():
        config = config_path.read_text()
        if config_path in config: pass
        else: config_path.write_text(config + "\n" + config_path)
    else:
        config_path.delete(sure=True)  # delete a bad symlink if any
        config_path.write_text(config_patch)


if __name__ == '__main__':
    main()
    # pass

