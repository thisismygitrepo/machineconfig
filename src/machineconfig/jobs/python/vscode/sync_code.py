from pathlib import Path
from configparser import SectionProxy
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from machineconfig.utils.io import read_ini

config = read_ini(Path.home().joinpath(".ssh", "config"))


def sync_remote(machine_name: str) -> None:
    console = Console()
    console.print(
        Panel.fit(
            "\n".join([f"🖥️  Target machine: {machine_name}"]),
            title="🔄 Sync Remote",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    machine_config: SectionProxy | None = None
    if machine_name in config:
        machine_config = config[machine_name]

    if machine_config is None:
        error_msg = f"Machine {machine_name} not found in SSH config."
        console.print(
            Panel.fit(
                "\n".join([error_msg]),
                title="❌ Error",
                subtitle="⚠️ Unknown target machine",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        raise ValueError(error_msg)

    code = f"""
ssh -o "HostName={machine_config["HostName"]}" -o "User={machine_config["User"]}" -o "ProxyCommand=cloudflared access ssh --hostname %h" -o "Port={machine_config["Port"]}" -o "RequestTTY=yes" -o "RemoteCommand=devops --which update; bash" {machine_name}
"""

    syntax = Syntax(code, "bash", line_numbers=False, word_wrap=True)
    console.print(
        Panel(
            syntax,
            title=f"🔄 Sync Command | {machine_name}",
            subtitle=f"🌐 Host: {machine_config['HostName']}",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    code_path = Path.home().joinpath(".config", "machingconfig", "vscode_api", "code_temp")
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code, encoding="utf-8")
    code_path.chmod(0o755)

    console.print(f"🚀 Executing sync command for {machine_name}...", style="bold yellow")

    import subprocess

    subprocess.run([str(code_path)], shell=True, check=True)

    console.print(
        Panel.fit(
            "\n".join([f"🖥️  Machine: {machine_name}"]),
            title="✅ Sync Completed",
            border_style="green",
            box=box.ROUNDED,
        )
    )
