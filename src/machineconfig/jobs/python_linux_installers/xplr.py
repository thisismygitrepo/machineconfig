

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/sayanarijit/xplr")
release = get_latest_release(repo_url.as_url_str())
path = release.joinpath(f"xplr-linux.tar.gz").download().ungz_untar(inplace=True)
exe = path.joinpath("xplr")
exe.chmod(0o777)
# exe.move(folder=r"/usr/local/bin", overwrite=False)
tb.Terminal().run(f"mv {exe} /usr/local/bin/").print()

