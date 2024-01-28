
"""SSH
"""


from platform import system
from machineconfig.utils.utils import LIBRARY_ROOT, display_options
from crocodile.file_management import P


def get_add_ssh_key_script(path_to_key: P):
    if system() == "Linux": authorized_keys = P.home().joinpath(".ssh/authorized_keys")
    elif system() == "Windows": authorized_keys = P("C:/ProgramData/ssh/administrators_authorized_keys")
    else: raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        print(f'ℹ️ Users that can access this machine have private keys of those pub keys:\n{authorized_keys.read_text().split(split)}')

        if path_to_key.read_text() in authorized_keys.read_text():
            print(f"⚠️ Key {path_to_key} already added to {authorized_keys}. No action is taken.")
            program = ""
        else:
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            elif system() == "Windows":
                program_path = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
                program = program_path.expanduser().read_text()
                place_holder = r'$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"'
                assert place_holder in program, f"This section performs string manipulation on the script {program_path} to add the key to the authorized_keys file. The script has changed and the string {place_holder} is not found."
                program = program.replace(place_holder, f'$sshfile = "{path_to_key}"')
                print(f"Replaced {place_holder} with {path_to_key} in {program_path}.")
            else: raise NotImplementedError
    else:
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program = LIBRARY_ROOT.joinpath("setup_windows/openssh-server_add-sshkey.ps1")
            program = P(program).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')

    if system() == "Linux": program += f"""

sudo chmod 700 ~/.ssh
sudo chmod 644 ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/*.pub
sudo service ssh --full-restart
# from superuser.com/questions/215504/permissions-on-private-key-in-ssh-folder

"""
    return program


def main():
    pub_keys = P.home().joinpath(".ssh").search("*.pub")
    all_keys_option = f"all pub keys available ({len(pub_keys)})"
    i_have_path_option = "I have the path to the key file"
    i_paste_option = "I want to paste the key itself"
    res = display_options("Which public key to add? ", options=pub_keys.apply(str).list + [all_keys_option, i_have_path_option, i_paste_option])
    assert isinstance(res, str), f"Got {res} of type {type(res)} instead of str."
    if res == all_keys_option: program = "\n\n\n".join(pub_keys.apply(get_add_ssh_key_script))
    elif res == i_have_path_option: program = get_add_ssh_key_script(P(input("Path: ")).expanduser().absolute())
    elif res == i_paste_option: program = get_add_ssh_key_script(P.home().joinpath(f".ssh/{input('file name (default: my_pasted_key.pub): ') or 'my_pasted_key.pub'}").write_text(input("Paste the pub key here: ")))
    else:
        program = get_add_ssh_key_script(P(res))
        print(program)
    return program


if __name__ == '__main__':
    pass
