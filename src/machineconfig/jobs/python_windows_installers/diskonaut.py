
import crocodile.toolbox as tb
dir_ = r"https:\drive.google.com\file\d\1XMXD4A0BWP8MuBSWOLHlI19Gzlb_vERm"
tb.P(dir_).download(name="diskonaut.exe").move(folder=tb.get_env().WindowsApps, overwrite=True)
