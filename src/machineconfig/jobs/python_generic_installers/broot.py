

# wget https://dystroy.org/broot/download/x86_64-linux/broot
# # broot is an fzf variant. It's excellent for viewing folder structure and layered search.
# # broot doesn't search aribtrarily deep and it also avoids git folders.
# chmod +x broot
# sudo mv ./broot /usr/local/bin/

import crocodile.toolbox as tb
from rich.console import Console
from platform import system

if system() == 'Linux':
    url = r'https://dystroy.org/broot/download/x86_64-linux/broot'
elif system() == 'Windows':
    url = r'https://dystroy.org/broot/download/x86_64-pc-windows-gnu/broot.exe'
else:
    raise Exception(f"Unsupported OS: {system()}")


def main():
    print("\n\n\n")
    console = Console()
    console.rule("Installing Broot")

    if system() == "Windows":
        p = tb.P(url).download()
        p.move(folder=tb.get_env().WindowsApps, overwrite=True)
    else:
        p = tb.P(url).download()
        p.chmod(0o777)  # p.move(folder=r'/usr/local/bin/', overwrite=True) Permission Error
        tb.Terminal().run(f"sudo mv {p} /usr/local/bin/").print()

    console.rule("Completed Installation")


if __name__ == '__main__':
    main()
