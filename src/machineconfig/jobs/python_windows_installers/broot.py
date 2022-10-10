
import crocodile.toolbox as tb

p = tb.P(r'https://dystroy.org/broot/download/x86_64-pc-windows-gnu/broot.exe').download()
p.move(folder=tb.get_env().WindowsApps, overwrite=True)
