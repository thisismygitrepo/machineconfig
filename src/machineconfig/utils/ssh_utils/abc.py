

from typing import Literal
def get_uv_run_command(platform: Literal["Windows", "Linux", "Darwin"]) -> str:
    UV_RUN_CMD = """$HOME/.local/bin/uv run """ if platform != "Windows" else """& "$env:USERPROFILE/.local/bin/uv" run"""
    return UV_RUN_CMD


MACHINECONFIG_VERSION = "machineconfig>=7.85"
DEFAULT_PICKLE_SUBDIR = "tmp_results/tmp_scripts/ssh"

