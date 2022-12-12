

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb


def main():
    repo_url = tb.P(r"https://github.com/atanunq/viu")
    release = get_latest_release(repo_url.as_url_str())
    exe = release.joinpath(f"viu").download()
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print()


if __name__ == '__main__':
    pass
