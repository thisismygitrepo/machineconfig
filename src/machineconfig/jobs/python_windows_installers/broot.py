
import crocodile.toolbox as tb

print("\n\n\n")
print("Installing Broot".center(100, "-"))
p = tb.P(r'https://dystroy.org/broot/download/x86_64-pc-windows-gnu/broot.exe').download()
p.move(folder=tb.get_env().WindowsApps, overwrite=True)
print("Completed Installation".center(100, "-"))
