from machineconfig.utils.installer import get_latest_release
from platform import system
from typing import Optional


repo_url = "https://github.com/Byron/dua-cli"
__doc__ = """Rust-based cli tool to get a quick overview of disk usage."""


def main(version: Optional[str] = None) -> None:
    if system() == 'Windows':
        suffix = "x86_64-pc-windows-msvc"
        _ = get_latest_release(repo_url, exe_name="dua", tool_name="dua", suffix=suffix, download_n_extract=True, delete=False, strip_v=False, compression="zip", version=version)
    else:
        suffix = "x86_64-unknown-linux-musl"
        _ = get_latest_release(repo_url, exe_name="dua", tool_name="dua", download_n_extract=True, delete=True, suffix=suffix, compression="tar.gz", version=version)
    return None


if __name__ == '__main__':
    main()
