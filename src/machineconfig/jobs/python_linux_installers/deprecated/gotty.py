from machineconfig.utils.installer import get_latest_release
# import crocodile.toolbox as tb
from typing import Optional


repo_url = r'https://github.com/sorenisanerd/gotty'
suffix = 'linux_amd64'
__doc__ = """gotty is a simple command line tool that turns your CLI tools into web applications."""


def main(version: Optional[str] = None):
    release = get_latest_release(repo_url=repo_url, exe_name="gotty", suffix=suffix, version=version, download_n_extract=True, compression="tar.gz", sep="_")
    return release


if __name__ == '__main__':
    main()
