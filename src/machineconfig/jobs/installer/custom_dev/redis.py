"""nedis installer"""

import platform
import subprocess
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData

# config_dict: InstallerData = {"appName": "Redis", "repoURL": "CMD", "doc": "submillisecond fast key-value db"}


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    print(f"""
{"=" * 150}
🗃️  REDIS INSTALLER | Setting up in-memory database
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        error_msg = "Redis installation not supported on Windows through this installer"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
💡 TIP: Consider using WSL2 or Docker to run Redis on Windows
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        print(f"🐧 Installing Redis on {system_name} using installation script...")
        import machineconfig.jobs.installer as module
        from pathlib import Path
        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("linux_scripts/redis.sh").read_text(encoding="utf-8")
        else:  # Darwin/macOS
            program = "brew install redis"
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
ℹ️  INFO | Redis features:
⚡ In-memory data structure store
🔑 Key-value database with optional persistence
🚀 Sub-millisecond response times
💾 Supports strings, lists, sets, sorted sets, hashes
🔄 Built-in replication and Lua scripting
{"=" * 150}
""")

    print("🔄 EXECUTING | Running Redis installation...")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        print("✅ Redis installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
