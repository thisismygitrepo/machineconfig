

from typing import TypedDict, Literal, TypeAlias


CATEGORY: TypeAlias = Literal["OS_SPECIFIC", "OS_GENERIC", "CUSTOM", "OS_SPECIFIC_DEV", "OS_GENERIC_DEV", "CUSTOM_DEV"]


class InstallerData(TypedDict):
    appName: str
    repoURL: str
    doc: str
    filenameTemplateWindowsAmd64: str
    filenameTemplateWindowsArm64: str
    filenameTemplateLinuxAmd64: str
    filenameTemplateLinuxArm64: str
    filenameTemplateMacosAmd64: str
    filenameTemplateMacosArm64: str
    stripVersion: bool
    exeName: str

class InstallerDataFiles(TypedDict):
    version: str
    installers: list[InstallerData]
