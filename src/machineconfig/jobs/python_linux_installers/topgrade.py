

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb


def main():
    repo_url = tb.P(r"https://github.com/topgrade-rs/topgrade")
    _ = get_latest_release(repo_url.as_url_str(), suffix='x86_64-unknown-linux-gnu', compression='tar.gz', linux=True, strip_v=False, download_n_extract=True)


if __name__ == '__main__':
    main()
