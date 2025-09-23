from pathlib import Path
from configparser import SectionProxy
from machineconfig.utils.utils2 import read_ini

config = read_ini(Path.home().joinpath(".ssh", "config"))


def sync_remote(machine_name: str):
    print(f"""
{"=" * 150}
🔄 SYNC REMOTE | Initiating remote code synchronization
🖥️  Target machine: {machine_name}
{"=" * 150}
""")

    # Handle config as a ConfigParser object
    machine_config: SectionProxy | None = None
    if machine_name in config:
        machine_config = config[machine_name]

    if machine_config is None:
        error_msg = f"Machine {machine_name} not found in SSH config."
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise ValueError(error_msg)

    code = f"""
ssh -o "HostName={machine_config["HostName"]}" -o "User={machine_config["User"]}" -o "ProxyCommand=cloudflared access ssh --hostname %h" -o "Port={machine_config["Port"]}" -o "RequestTTY=yes" -o "RemoteCommand=devops --which update; bash" {machine_name}
"""
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel

    console = Console()
    console.print(f"\n{'=' * 150}")
    console.print(Panel(Syntax(code, lexer="bash"), title=f"🔄 SYNC COMMAND | Connecting to {machine_name}", subtitle=f"🌐 Host: {machine_config['HostName']}"), style="bold blue")
    console.print(f"{'=' * 150}\n")

    code_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", "code_temp")
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code, encoding="utf-8")
    code_path.chmod(0o755)

    print(f"🚀 Executing sync command for {machine_name}...")

    import subprocess

    subprocess.run([str(code_path)], shell=True, check=True)

    print(f"""
{"=" * 150}
✅ SUCCESS | Remote sync completed successfully
🖥️  Machine: {machine_name}
{"=" * 150}
""")
