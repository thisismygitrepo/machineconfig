

import platform

UV_RUN_CMD = "$HOME/.local/bin/uv run" if platform.system() != "Windows" else """& "$env:USERPROFILE/.local/bin/uv" run"""
MACHINECONFIG_VERSION = "machineconfig>=7.82"
DEFAULT_PICKLE_SUBDIR = "tmp_results/tmp_scripts/ssh"

