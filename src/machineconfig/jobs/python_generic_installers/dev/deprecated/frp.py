
from machineconfig.utils.installer import get_latest_release
from platform import system
from typing import Optional

__doc__ = """Rust-based cli tool to get a quick overview of disk usage."""
repo_url  = rf"https://github.com/fatedier/frp"


def main(version: Optional[str] = None):
    _ = version
    if system() == "Windows":
        res = get_latest_release(repo_url=repo_url, exe_name="frp", strip_v=True, sep="_", download_n_extract=False, suffix="windows_amd64")
        if res is not None:
            res = res.unzip(inplace=True)
            # exe.move(folder=P.get_env().WindowsApps, overwrite=True)  # latest version overwrites older installation.
            # res.delete(sure=True)
    elif system() == "Linux":
        res = get_latest_release(repo_url=repo_url, exe_name="frp", strip_v=True, sep="_", download_n_extract=False, suffix="linux_amd64", compression="tar.gz")
        if res is not None:
            res = res.ungz_untar(inplace=True)
            # exe.chmod(0o777)
            # # exe.move(folder=r"/usr/local/bin", overwrite=False)
            # Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
            # res.delete(sure=True)
    else:
        raise NotImplementedError(f"System `{system()}` not supported.")
    _ = res
    return ""


if __name__ == '__main__':
    main()