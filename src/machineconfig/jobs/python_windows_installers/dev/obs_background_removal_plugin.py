
# this is a plugin for OBS Studio to remove background from a video

from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb


url = "https://github.com/royshil/obs-backgroundremoval"


def main(version=None):
    link = get_latest_release(url, download_n_extract=False, version=version)
    link = link.joinpath(f"obs-backgroundremoval-{link.parts[-1][1:]}-win64.zip").download()
    # link.search(r=True, folders=False).apply(lambda file: file.move(tb.P(fr"C:/Program Files/obs-studio").joinpath(file.relative_to(link)), overwrite=True))
    # Expand-Archive {link} -DestinationPath 'C:\Program Files\obs-studio\' -Force


if __name__ == '__main__':
    main()
