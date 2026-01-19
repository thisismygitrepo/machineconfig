r"""ID

On windows:

$sshfile = "$env:USERPROFILE/.ssh/id_rsa"
Set-Service ssh-agent -StartupType Manual  # allow the service to be started manually
ssh-agent  # start the service
ssh-add.exe $sshfile # add the key to the agent

# copy ssh key:
# This is the Windows equivalent of copy-ssh-id on Linux.
# Just like the original function, it is a convenient way of doing two things in one go:
# 1- copy a certain public key to the remote machine.
#    scp ~/.ssh/id_rsa.pub $remote_user@$remote_host:~/.ssh/authorized_keys
# 2- Store the value on the remote in a file called .ssh/authorized_keys
#    ssh $remote_user@$remote_host "echo $public_key >> ~/.ssh/authorized_keys"
# Idea from: https://www.chrisjhart.com/Windows-10-ssh-copy-id/



"""

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.options import choose_from_options
from rich.console import Console
from rich.panel import Panel


console = Console()


def main() -> None:
    private_keys = [PathExtended(x).with_name(x.stem) for x in PathExtended.home().joinpath(".ssh").glob("*.pub")]
    key_status = f"Found {len(private_keys)} key(s)" if private_keys else "No keys found"
    console.print(Panel(f"🔑 SSH Identity Management\n🔍 {key_status} in ~/.ssh", title="[bold blue]Setup[/bold blue]", expand=False))

    choice = choose_from_options(msg="Path to private key to be used when ssh'ing: ", options=[str(x) for x in private_keys] + ["I have the path to the key file", "I want to paste the key itself"], multi=False)

    if choice == "I have the path to the key file":
        path_to_key = PathExtended(input("📋 Enter path to private key: ")).expanduser().absolute()
    elif choice == "I want to paste the key itself":
        key_filename = input("📝 File name (default: my_pasted_key): ") or "my_pasted_key"
        path_to_key = PathExtended.home().joinpath(f".ssh/{key_filename}")
        path_to_key.parent.mkdir(parents=True, exist_ok=True)
        path_to_key.write_text(input("🔑 Paste the private key: "), encoding="utf-8")
    else:
        path_to_key = PathExtended(choice)

    txt = f"IdentityFile {path_to_key.collapseuser().as_posix()}"
    config_path = PathExtended.home().joinpath(".ssh/config")

    if config_path.exists():
        current = config_path.read_text(encoding="utf-8")
        config_action = "updated"
    else:
        current = txt
        config_action = "created"
    lines = current.split("\n")
    found = False
    for i, line in enumerate(lines):
        if txt in line:
            lines[i] = txt
            found = True
    if not found:
        lines.insert(0, txt)
    config_path.write_text("\n".join(lines), encoding="utf-8")

    console.print(Panel(f"✅ Identity: {path_to_key.name}\n📄 Config {config_action}: {config_path}", title="[bold green]Complete[/bold green]", expand=False, border_style="green"))
    return None


if __name__ == "__main__":
    pass
