"""nedis installer
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "submillisecond fast key-value db",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "redis"
}


def main(version: Optional[str]):
    print(f"""
{'=' * 70}
🗃️  REDIS INSTALLER | Setting up in-memory database
💻 Platform: {platform.system()}
🔄 Version: {'latest' if version is None else version}
{'=' * 70}
""")
    
    _ = version
    if platform.system() == "Windows":
        error_msg = "Redis installation not supported on Windows through this installer"
        print(f"""
{'⚠️' * 20}
❌ ERROR | {error_msg}
💡 TIP: Consider using WSL2 or Docker to run Redis on Windows
{'⚠️' * 20}
""")
        raise NotImplementedError(error_msg)
    elif platform.system() == "Linux":
        print("🐧 Installing Redis on Linux using installation script...")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path
        program = Path(module.__file__).parent.joinpath("scripts/linux/redis.sh").read_text(encoding="utf-8")
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{'⚠️' * 20}
❌ ERROR | {error_msg}
{'⚠️' * 20}
""")
        raise NotImplementedError(error_msg)
    
    print(f"""
{'=' * 70}
ℹ️  INFO | Redis features:
⚡ In-memory data structure store
🔑 Key-value database with optional persistence
🚀 Sub-millisecond response times
💾 Supports strings, lists, sets, sorted sets, hashes
🔄 Built-in replication and Lua scripting
{'=' * 70}
""")
    
    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass

