"""docker installer"""

import platform
from typing import Optional


config_dict = {"repo_url": "CUSTOM", "doc": "lightweight containerization", "filename_template_windows_amd_64": "", "filename_template_linux_amd_64": "", "strip_v": False, "exe_name": "docker"}


def main(version: Optional[str]):
    print(f"""
{"=" * 150}
🐳 DOCKER INSTALLER | Setting up containerization platform
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        error_msg = "Docker installation not supported on Windows through this installer"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
💡 TIP: Please use Docker Desktop for Windows instead
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        print(f"🐧 Installing Docker on {system_name} using official script...")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path

        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("scripts/linux/docker.sh").read_text(encoding="utf-8")
        else:  # Darwin/macOS
            # For macOS, we'll use the same script or recommend Homebrew
            program = "brew install --cask docker"
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"=" * 150}
ℹ️  INFO | Docker features:
📦 Container-based virtualization
🚀 Simplified application deployment
🔄 Consistent development environments
🛡️ Isolated application environments
📊 Efficient resource utilization
{"=" * 150}
""")

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
