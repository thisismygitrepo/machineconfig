
"""brave installer
"""

import platform
from typing import Optional


config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Chrome with no ads",
        "filename_template_windows_amd_64": "",
        "filename_template_linux_amd_64": "",
        "strip_v": False,
        "exe_name": "brave"
}



def main(version: Optional[str]):
    _ = version
    if platform.system() == "Windows":
        program = """

winget install --Name "Brave Browser" --Id Brave.Brave --source winget --accept-package-agreements --accept-source-agreements

"""
    elif platform.system() == "Linux":
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path
        program = Path(module.__file__).parent.joinpath("scripts/linux/brave.sh").read_text(encoding="utf-8")
    else:
        raise NotImplementedError("unsupported platform")
    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass

