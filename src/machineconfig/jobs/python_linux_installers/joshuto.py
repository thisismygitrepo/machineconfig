

"""
Rust version of FZF (GO)
"""
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb

# repo_url = tb.P(r"https://github.com/kamiyaa/joshuto")
# release = get_latest_release(repo_url.as_url_str())
# path = release.joinpath(f"joshuto-{release[-1]}-x86_64-unknown-linux-gnu.tar.gz")

# pre-release
path = tb.P(r'https://github.com/kamiyaa/joshuto/releases/download/v0.9.4/joshuto-v0.9.4-x86_64-unknown-linux-gnu.tar.gz')
path = path.download().ungz_untar(inplace=True)
exe = path.search()[0].joinpath("joshuto")
exe.chmod(0o777)
# exe.move(folder=r"/usr/local/bin/", overwrite=False)
tb.Terminal().run(f"mv {exe} /usr/local/bin/").print()

