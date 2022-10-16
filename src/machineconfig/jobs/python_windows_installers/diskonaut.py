
print("\n\n\n")
print("Installing Broot".center(100, "-"))
import crocodile.toolbox as tb
# after cargo install diskonaut
# then mv ~/.cargo/bin/diskonaut.exe ~/AppData/Local/Microsoft/WindowsApps/
# then bu_gdrive_sx.ps1 .\diskonaut.exe -sRz  # zipping is vital to avoid security layers and keep file metadata.
url = r'https://drive.google.com/uc?id=1MsDaW6JXmS1LVyfThtUuJy4WRxODEjZB&export=download'
dir_ = tb.P(url).download(name='diskonaut.zip').unzip(inplace=True)
dir_.search()[0].move(folder=tb.get_env().WindowsApps, overwrite=True)
dir_.delete(sure=True)
print("Completed Installation".center(100, "-"))
