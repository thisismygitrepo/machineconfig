
"""
Rust version of FZF (GO)
"""
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb

repo_url = tb.P(r"https://github.com/lotabout/skim")
release = get_latest_release(repo_url.as_url_str())
path = release.joinpath(f"skim-{release[-1]}-x86_64-unknown-linux-musl.tar.gz").download().ungz_untar(inplace=True)
exe = path.joinpath("sk")
exe.chmod(0o777)
# exe.move(folder=r"/usr/local/bin", overwrite=False)
tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print()

