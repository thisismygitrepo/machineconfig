
import crocodile.toolbox as tb
# fd (rust)
# cargo install fd-find
# search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf

url = 'https://github.com/ascii-boxes/boxes'

def main(version=None):
    from machineconfig.utils.utils import get_latest_release
    get_latest_release(url, suffix="intel-win32", download_n_extract=True, version=version, strip_v=True, delete=False)
    tb.P.home().joinpath(f"Downloads").search("boxes.cfg", r=True)[0].move(folder=tb.P.get_env().WindowsApps)


if __name__ == '__main__':
    main()
