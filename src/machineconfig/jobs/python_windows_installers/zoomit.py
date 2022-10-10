
import crocodile.toolbox as tb
folder = tb.P(r'https://download.sysinternals.com/files/ZoomIt.zip').download(tb.P.home().joinpath('Downloads')).unzip(inplace=True)
folder.joinpath('ZoomIt.exe').move(folder=tb.get_env().WindowsApps, overwrite=True)
folder.delete(sure=True)
