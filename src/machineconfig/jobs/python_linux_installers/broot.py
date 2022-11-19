

# wget https://dystroy.org/broot/download/x86_64-linux/broot
# # broot is an fzf variant. It's excellent for viewing folder structure and layered search.
# # broot doesn't search aribtrarily deep and it also avoids git folders.
# chmod +x broot
# sudo mv ./broot /usr/local/bin/

import crocodile.toolbox as tb


url = r'https://dystroy.org/broot/download/x86_64-linux/broot'


def main():
    print("\n\n\n")
    print("Installing Broot".center(100, "-"))
    p = tb.P(url).download()
    p.chmod(0o777)
    # p.move(folder=r'/usr/local/bin/', overwrite=True) Permission Error
    tb.Terminal().run(f"sudo mv {p} /usr/local/bin/").print()
    print("Completed Installation".center(100, "-"))


if __name__ == '__main__':
    main()

