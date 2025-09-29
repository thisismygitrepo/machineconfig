from typing import TypedDict, Literal, TypeAlias, Optional
import platform


CPU_ARCHITECTURES: TypeAlias = Literal["amd64", "arm64"]
OPERATING_SYSTEMS: TypeAlias = Literal["windows", "linux", "macos"]


class InstallerData(TypedDict):
    appName: str
    doc: str
    repoURL: str
    fileNamePattern: dict[CPU_ARCHITECTURES, dict[OPERATING_SYSTEMS, Optional[str]]]


class InstallerDataFiles(TypedDict):
    version: str
    installers: list[InstallerData]


def get_os_name() -> OPERATING_SYSTEMS:
    """Get the operating system name in the format expected by the github parser."""
    sys_name = platform.system()
    if sys_name == "Windows":
        return "windows"
    elif sys_name == "Linux":
        return "linux"
    elif sys_name == "Darwin":
        return "macos"
    else:
        raise NotImplementedError(f"System {sys_name} not supported")


def get_normalized_arch() -> CPU_ARCHITECTURES:
    """Get the normalized CPU architecture."""
    arch_raw = platform.machine().lower()
    if arch_raw in ("x86_64", "amd64"):
        return "amd64" 
    if arch_raw in ("aarch64", "arm64", "armv8", "armv8l"):
        return "arm64"
    # Default to amd64 if unknown architecture
    return "amd64"
