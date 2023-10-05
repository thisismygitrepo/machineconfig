
"""SSH
"""

import crocodile.toolbox as tb
from platform import system
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def get_add_ssh_key_script(path_to_key: tb.P):
    if system() == "Linux": authorized_keys = tb.P.home().joinpath(".ssh/authorized_keys")
    elif system() == "Windows": authorized_keys = tb.P("C:/ProgramData/ssh/administrators_authorized_keys")
    else: raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        print(f'Users that can access this machine have private keys of those pub keys:\n{authorized_keys.read_text().split(split)}')

        if path_to_key.read_text() in authorized_keys.read_text():
            program = ""
        else:
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            else:
                program = LIBRARY_ROOT.joinpath("jobs/windows/openssh-server_add_sshkey.ps1")
                program = tb.P(program).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')

    else:
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program = LIBRARY_ROOT.joinpath("jobs/windows/openssh-server_add_sshkey.ps1")
            program = tb.P(program).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')

    if system() == "Linux" and 2 > 1: program += f"""

sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder

"""
    return program


def main():
    pub_keys = tb.P.home().joinpath(".ssh").search("*.pub")
    res = display_options("Which public key to add? ", options=pub_keys.apply(str).list + [f"all pub keys available ({len(pub_keys)})", "I have the path to the key file", "I want to paste the key itself"])
    assert isinstance(res, str), f"Got {res} of type {type(res)} instead of str."
    if res == "all": program = "\n\n\n".join(pub_keys.apply(get_add_ssh_key_script))
    elif res == "I have the path to the key file": program = get_add_ssh_key_script(tb.P(input("Path: ")).expanduser().absolute())
    elif res == "I want to paste the key itself": program = get_add_ssh_key_script(tb.P.home().joinpath(f".ssh/{input('file name (default: my_pasted_key.pub): ') or 'my_pasted_key.pub'}").write_text(input("Paste the pub key here: ")))
    else: program = get_add_ssh_key_script(tb.P(res))
    return program


if __name__ == '__main__':
    pass
