
import crocodile.toolbox as tb
from platform import system


def get_add_ssh_key_script(path_to_key):
    if system() == "Linux": authorized_keys = tb.P.home().joinpath(".ssh/authorized_keys")
    elif system() == "Windows": authorized_keys = tb.P("C:/ProgramData/ssh/administrators_authorized_keys")
    else: raise NotImplementedError

    if authorized_keys.exists():
        split = "\n"
        print(
            f'Users that can access this machine have private keys of those pub keys:\n{authorized_keys.read_text().split(split)}')

        if path_to_key.read_text() in authorized_keys.read_text():
            program = ""
        else:
            if system() == "Linux":
                program = f"cat {path_to_key} >> ~/.ssh/authorized_keys"
            else:
                program = "~/code/machineconfig/src/machineconfig/jobs/windows/openssh-server_add_key.ps1"
                program = tb.P(program).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')

    else:
        if system() == "Linux":
            program = f"cat {path_to_key} > ~/.ssh/authorized_keys"
        else:
            program = "~/code/machineconfig/src/machineconfig/jobs/windows/openssh-server_add_key.ps1"
            program = tb.P(program).expanduser().read_text().replace('$sshfile=""', f'$sshfile="{path_to_key}"')
    return program

