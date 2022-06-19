"""
This is the first file that should you should to setup a new machine once you get SSH connection to it.

"""

import crocodile.toolbox as tb


def main(username, hostname, source):
    """Copy dotfiles  over to the remote machine."""
    client = tb.meta.SSH(hostname=hostname, username=username)
    client.copy_from_here(source=source, zip_n_encrypt=True)
    # client.copy_from_here("./setup_linux.bash", target="~")
    # client.execute("bash setup_linux.bash")  # there is interactive prompt


if __name__ == '__main__':
    pass
