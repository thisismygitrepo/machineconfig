"""warp-cli installer"""

import platform
from typing import Optional


config_dict = {"repo_url": "CUSTOM", "doc": "cli for warp from cloudflare", "filename_template_windows_amd_64": "", "filename_template_linux_amd_64": "", "strip_v": False, "exe_name": "warp-cli"}


def main(version: Optional[str]):
    print(f"""
{"═" * 150}
🌐 CLOUDFLARE WARP | Installing Cloudflare WARP CLI
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"═" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        error_msg = "WARP CLI installation not supported on Windows through this installer"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
💡 TIP: Please download and install manually from Cloudflare website
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() in ["Linux", "Darwin"]:
        print("""
🐧 LINUX SETUP | Installing Cloudflare WARP CLI using installation script...
""")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path

        program = Path(module.__file__).parent.joinpath("scripts/linux/warp-cli.sh").read_text(encoding="utf-8")
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"═" * 150}
ℹ️  INFO | Cloudflare WARP Features:
🔒 Secure your internet connection
🚀 Improve browsing performance
🛡️ Hide your IP address
🔐 Encrypt your DNS queries
🌐 Access Cloudflare Zero Trust services
{"═" * 150}
""")

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
