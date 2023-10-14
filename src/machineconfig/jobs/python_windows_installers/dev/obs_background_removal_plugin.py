
# this is a plugin for OBS Studio to remove background from a video

from machineconfig.utils.utils import P
from machineconfig.utils.installer import get_latest_release
from typing import Optional


url = "https://github.com/royshil/obs-backgroundremoval"
__doc__ = """A plugin for OBS Studio to remove background from a video"""


def main(version: Optional[str] = None):
    link = get_latest_release(repo_url=url, exe_name="obs", download_n_extract=False, version=version)
    if not isinstance(link, P): raise ValueError(f"Failed to get latest release. Expected a Path object, got {link}")
    link = link.joinpath(f"obs-backgroundremoval-{link.parts[-1][1:]}-win64.zip").download()
    # link.search(r=True, folders=False).apply(lambda file: file.move(tb.P(fr"C:/Program Files/obs-studio").joinpath(file.relative_to(link)), overwrite=True))
    # Expand-Archive {link} -DestinationPath 'C:\Program Files\obs-studio\' -Force


if __name__ == '__main__':
    main()
