


from crocodile.core import Read
from pathlib import Path

config = Read.ini(Path.home().joinpath(".ssh", "config"))
if config is None:
    raise ValueError("SSH config not found. Please create one first.")


def sync_remote(machine_name: str):
    machine_config = config.get(machine_name)
    if machine_config is None:
        raise ValueError(f"Machine {machine_name} not found in SSH config.")

    # this is template: code = """ssh -o "HostName=zgeby8zhe6ipftpad.alexsaffar.com" -o "User=alex" -o "ProxyCommand=cloudflared access ssh --hostname %h" -o "Port=443" -o "RequestTTY=yes" -o "RemoteCommand=bash ~/scripts/z_ls --attach; bash" tpadCF"""
    code = f"""
ssh -o "HostName={machine_config['HostName']}" -o "User={machine_config['User']}" -o "ProxyCommand=cloudflared access ssh --hostname %h" -o "Port={machine_config['Port']}" -o "RequestTTY=yes" -o "RemoteCommand=devops --which update; bash" {machine_name}
"""
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.panel import Panel
    from rich.console import Console

    console = Console()
    console.print(Panel(Syntax(code, lexer="bash"), title='Sync remote'), style="bold red")

    code_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", "code_temp")
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code, encoding="utf-8")
    code_path.chmod(0o755)
    import subprocess
    subprocess.run([str(code_path)], shell=True, check=True)

