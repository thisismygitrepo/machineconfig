

from machineconfig.utils.utils import get_latest_release
from platform import system
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/mgunyho/tere")


if system() == 'Windows':
    from crocodile.environment import AppData
    target = AppData
    suffix = "x86_64-pc-windows-gnu"
    exe = get_latest_release(repo_url.as_url_str(), suffix=suffix, download_n_extract=True, delete=False, strip_v=True)
else:
    release = get_latest_release(repo_url.as_url_str())
    path = release.joinpath(f"tere-{str(release[-1]).replace('v', '')}-x86_64-unknown-linux-gnu.zip").download()
    exe = path.unzip(inplace=True).joinpath("tere")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    tb.Terminal().run(f"mv {exe} /usr/local/bin/").print()

