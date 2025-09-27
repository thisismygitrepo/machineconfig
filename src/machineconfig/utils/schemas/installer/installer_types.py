from typing import TypedDict, Literal, TypeAlias


APP_INSTALLER_CATEGORY: TypeAlias = Literal["OS_SPECIFIC", "OS_GENERIC", "CUSTOM", "OS_SPECIFIC_DEV", "OS_GENERIC_DEV", "CUSTOM_DEV"]
CPU_ARCHITECTURES: TypeAlias = Literal["amd64", "arm64"]
OPERATING_SYSTEMS: TypeAlias = Literal["windows", "linux", "macos"]


class InstallerData(TypedDict):
    appName: str
    doc: str
    repoURL: str


class InstallerDataFiles(TypedDict):
    version: str
    installers: list[InstallerData]
