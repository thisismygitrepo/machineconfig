
# this is a plugin for OBS Studio to remove background from a video

from machineconfig.utils.utils import get_latest_release, tb


url = "https://github.com/royshil/obs-backgroundremoval"


def main():
    link = get_latest_release(url, download_n_extract=False)
    link = link.joinpath(f"obs-backgroundremoval-{link.parts[-1][1:]}-win64.zip").download().unzip()
    link.search(r=True, folders=False).apply(lambda file: file.move(tb.P(fr"C:/Program Files/obs-studio").joinpath(file.relative_to(link)), overwrite=True))


if __name__ == '__main__':
    main()
