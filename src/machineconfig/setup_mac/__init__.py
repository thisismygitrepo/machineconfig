"""Mac setup module for machineconfig.

This module provides setup script locations and configurations for macOS systems.
It mirrors the layout used by the Linux setup module and exposes Path objects
pointing at common scripts (so other code can import these paths).
"""

from pathlib import Path


# Optional helper scripts (may or may not exist)
UV = Path(__file__).parent.joinpath("uv.sh")
# Path to macOS SSH helper

