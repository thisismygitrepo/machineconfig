"""Machine Status Display - Comprehensive system and configuration overview"""

import platform
import shutil
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import CONFIG_ROOT, DEFAULTS_PATH, LIBRARY_ROOT


console = Console()



def _check_shell_profile_status() -> dict[str, Any]:
    """Check shell profile configuration status."""
    from machineconfig.profile.create_shell_profile import get_shell_profile_path

    try:
        profile_path = get_shell_profile_path()
        if not profile_path.exists():
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            profile_path.touch()
        profile_content = profile_path.read_text(encoding="utf-8")
        system_name = platform.system()
        if system_name == "Windows":
            init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/pwsh/init.ps1")
            init_script_copy = PathExtended(CONFIG_ROOT).joinpath("profile/init.ps1").collapseuser()
            source_reference = f". {str(init_script.collapseuser()).replace('~', '$HOME')}"
            source_copy = f". {str(init_script_copy).replace('~', '$HOME')}"
        else:
            init_script = PathExtended(CONFIG_ROOT).joinpath("settings/shells/bash/init.sh")
            init_script_copy = PathExtended(CONFIG_ROOT).joinpath("profile/init.sh").collapseuser()
            source_reference = f"source {str(init_script.collapseuser()).replace('~', '$HOME')}"
            source_copy = f"source {str(init_script_copy).replace('~', '$HOME')}"

        configured = source_reference in profile_content or source_copy in profile_content
        method = "reference" if source_reference in profile_content else ("copy" if source_copy in profile_content else "none")

        return {
            "profile_path": str(profile_path),
            "exists": True,
            "configured": configured,
            "method": method,
            "init_script_exists": init_script.exists(),
            "init_script_copy_exists": init_script_copy.exists(),
        }
    except Exception as ex:
        return {
            "profile_path": "Error",
            "exists": False,
            "configured": False,
            "method": "error",
            "error": str(ex),
            "init_script_exists": False,
            "init_script_copy_exists": False,
        }


def _check_repos_status() -> dict[str, Any]:
    """Check configured repositories status."""
    from machineconfig.utils.io import read_ini

    try:
        repos_str = read_ini(DEFAULTS_PATH)["general"]["repos"]
        repo_paths = [Path(p.strip()).expanduser() for p in repos_str.split(",") if p.strip()]

        repos_info = []
        for repo_path in repo_paths:
            if not repo_path.exists():
                repos_info.append({"path": str(repo_path), "name": repo_path.name, "exists": False, "is_repo": False})
                continue

            try:
                import git

                repo = git.Repo(str(repo_path))
                repos_info.append(
                    {
                        "path": str(repo_path),
                        "name": repo_path.name,
                        "exists": True,
                        "is_repo": True,
                        "clean": not repo.is_dirty(untracked_files=True),
                        "branch": repo.active_branch.name if not repo.head.is_detached else "DETACHED",
                    }
                )
            except Exception:
                repos_info.append({"path": str(repo_path), "name": repo_path.name, "exists": True, "is_repo": False})

        return {"configured": True, "count": len(repos_info), "repos": repos_info}
    except (FileNotFoundError, KeyError, IndexError):
        return {"configured": False, "count": 0, "repos": []}


def _check_ssh_status() -> dict[str, Any]:
    """Check SSH configuration status."""
    ssh_dir = PathExtended.home().joinpath(".ssh")
    if not ssh_dir.exists():
        return {"ssh_dir_exists": False, "keys": [], "config_exists": False, "authorized_keys_exists": False, "known_hosts_exists": False}

    keys = []
    for pub_key in ssh_dir.glob("*.pub"):
        private_key = pub_key.with_suffix("")
        keys.append(
            {
                "name": pub_key.stem,
                "public_exists": True,
                "private_exists": private_key.exists(),
                "public_path": str(pub_key),
                "private_path": str(private_key),
            }
        )

    config_file = ssh_dir.joinpath("config")
    authorized_keys = ssh_dir.joinpath("authorized_keys")
    known_hosts = ssh_dir.joinpath("known_hosts")

    return {
        "ssh_dir_exists": True,
        "keys": keys,
        "config_exists": config_file.exists(),
        "authorized_keys_exists": authorized_keys.exists(),
        "known_hosts_exists": known_hosts.exists(),
        "ssh_dir_path": str(ssh_dir),
    }


def _check_config_files_status() -> dict[str, Any]:
    """Check public and private configuration files status."""
    from machineconfig.profile.create_links import read_mapper

    try:
        mapper = read_mapper()
        public_configs = list(mapper.get("public", {}).keys())
        private_configs = list(mapper.get("private", {}).keys())

        public_count = len(public_configs)
        private_count = len(private_configs)

        public_linked = 0
        for config_name in public_configs:
            for config_item in mapper["public"][config_name]:
                target_path = PathExtended(config_item["config_file_default_path"]).expanduser()
                if target_path.exists():
                    public_linked += 1
                    break

        private_linked = 0
        for config_name in private_configs:
            for config_item in mapper["private"][config_name]:
                target_path = PathExtended(config_item["config_file_default_path"]).expanduser()
                if target_path.exists():
                    private_linked += 1
                    break

        return {
            "public_count": public_count,
            "public_linked": public_linked,
            "private_count": private_count,
            "private_linked": private_linked,
            "public_configs": public_configs,
            "private_configs": private_configs,
        }
    except Exception as ex:
        return {
            "public_count": 0,
            "public_linked": 0,
            "private_count": 0,
            "private_linked": 0,
            "error": str(ex),
            "public_configs": [],
            "private_configs": [],
        }


def _check_important_tools() -> dict[str, dict[str, bool]]:
    """Check if important CLI tools are installed, organized by groups."""
    from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES

    group_status = {}
    for group_name, tools in PACKAGE_GROUP2NAMES.items():
        tool_status = {}
        for tool in tools:
            tool_status[tool] = shutil.which(tool) is not None
        group_status[group_name] = tool_status

    return group_status


def _check_backup_config() -> dict[str, Any]:
    """Check backup configuration status."""
    from machineconfig.utils.io import read_ini
    import tomllib

    try:
        cloud_config = read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"]
    except (FileNotFoundError, KeyError, IndexError):
        cloud_config = "Not configured"

    try:
        backup_file = LIBRARY_ROOT.joinpath("profile/backup.toml")
        if backup_file.exists():
            backup_data = tomllib.loads(backup_file.read_text(encoding="utf-8"))
            backup_items = list(backup_data.keys())
            backup_items_count = len(backup_items)
        else:
            backup_items = []
            backup_items_count = 0
    except Exception:
        backup_items = []
        backup_items_count = 0

    return {"cloud_config": cloud_config, "backup_items_count": backup_items_count, "backup_items": backup_items}


def _display_system_info(info: dict[str, str]) -> None:
    """Display system information panel."""
    console.rule("[bold blue]💻 System Information[/bold blue]")

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("🏠 Hostname", info["hostname"])
    table.add_row("💿 System", f"{info['system']} {info['release']}")
    table.add_row("🖥️  Machine", info["machine"])
    table.add_row("⚙️  Processor", info["processor"])
    table.add_row("🐍 Python", info["python_version"])
    table.add_row("👤 User", info["user"])

    console.print(Panel(table, title="System", border_style="blue", padding=(1, 2), expand=False))


def _display_shell_status(status: dict[str, Any]) -> None:
    """Display shell profile status panel."""
    console.rule("[bold green]🐚 Shell Profile[/bold green]")

    if "error" in status:
        console.print(Panel(f"❌ Error: {status['error']}", title="Shell Profile", border_style="red", padding=(1, 2), expand=False))
        return

    from rich.columns import Columns

    left_table = Table(show_header=False, box=None, padding=(0, 1))
    left_table.add_column("Item", style="cyan", no_wrap=True)
    left_table.add_column("Status")

    left_table.add_row("📄 Profile", status["profile_path"])
    left_table.add_row(f"{'✅' if status['exists'] else '❌'} Exists", str(status["exists"]))
    left_table.add_row(f"{'✅' if status['configured'] else '❌'} Configured", str(status["configured"]))

    right_table = Table(show_header=False, box=None, padding=(0, 1))
    right_table.add_column("Item", style="cyan", no_wrap=True)
    right_table.add_column("Status")

    right_table.add_row("🔧 Method", status["method"])
    right_table.add_row(f"{'✅' if status['init_script_exists'] else '❌'} Init (source)", str(status["init_script_exists"]))
    right_table.add_row(f"{'✅' if status['init_script_copy_exists'] else '❌'} Init (copy)", str(status["init_script_copy_exists"]))

    border_style = "green" if status["configured"] else "yellow"
    console.print(
        Panel(
            Columns([left_table, right_table], equal=True, expand=True),
            title="Shell Profile",
            border_style=border_style,
            padding=(1, 2),
            expand=False,
        )
    )


def _display_repos_status(status: dict[str, Any]) -> None:
    """Display configured repositories status."""
    console.rule("[bold cyan]📚 Configured Repositories[/bold cyan]")

    if not status["configured"]:
        console.print(Panel(f"⚠️  No repositories configured in {DEFAULTS_PATH}", title="Repositories", border_style="yellow", padding=(1, 2)))
        return

    if status["count"] == 0:
        console.print(Panel("ℹ️  No repositories configured", title="Repositories", border_style="blue", padding=(1, 2)))
        return

    table = Table(show_lines=True, header_style="bold cyan")
    table.add_column("Repository", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    for repo in status["repos"]:
        name = repo["name"]
        if not repo["exists"]:
            table.add_row(f"❌ {name}", "Missing", f"Path: {repo['path']}")
        elif not repo["is_repo"]:
            table.add_row(f"⚠️  {name}", "Not a repo", f"Path: {repo['path']}")
        else:
            status_icon = "✅" if repo["clean"] else "⚠️"
            status_text = "Clean" if repo["clean"] else "Uncommitted changes"
            table.add_row(f"{status_icon} {name}", status_text, f"Branch: {repo['branch']}")

    console.print(Panel(table, title=f"Repositories ({status['count']})", border_style="cyan", padding=(1, 2)))


def _display_ssh_status(status: dict[str, Any]) -> None:
    """Display SSH configuration status."""
    console.rule("[bold yellow]🔐 SSH Configuration[/bold yellow]")

    if not status["ssh_dir_exists"]:
        console.print(Panel("❌ SSH directory (~/.ssh) does not exist", title="SSH Status", border_style="red", padding=(1, 2), expand=False))
        return

    from rich.columns import Columns

    config_table = Table(show_header=False, box=None, padding=(0, 1))
    config_table.add_column("Item", style="cyan", no_wrap=True)
    config_table.add_column("Status")

    config_table.add_row("📁 Directory", status["ssh_dir_path"])
    config_table.add_row(f"{'✅' if status['config_exists'] else '❌'} Config", str(status["config_exists"]))
    config_table.add_row(f"{'✅' if status['authorized_keys_exists'] else '❌'} Auth Keys", str(status["authorized_keys_exists"]))
    config_table.add_row(f"{'✅' if status['known_hosts_exists'] else '❌'} Known Hosts", str(status["known_hosts_exists"]))

    config_panel = Panel(config_table, title="SSH Config", border_style="yellow", padding=(1, 2), expand=False)

    if status["keys"]:
        keys_table = Table(show_header=True, box=None, padding=(0, 1), show_lines=False, expand=False)
        keys_table.add_column("Key Name", style="bold cyan")
        keys_table.add_column("Pub", justify="center")
        keys_table.add_column("Priv", justify="center")

        for key in status["keys"]:
            pub_status = "✅" if key["public_exists"] else "❌"
            priv_status = "✅" if key["private_exists"] else "❌"
            keys_table.add_row(key["name"], pub_status, priv_status)

        keys_panel = Panel(keys_table, title=f"SSH Keys ({len(status['keys'])})", border_style="yellow", padding=(1, 2), expand=False)

        console.print(Columns([config_panel, keys_panel], equal=False, expand=True))
    else:
        console.print(config_panel)


def _display_config_files_status(status: dict[str, Any]) -> None:
    """Display configuration files status."""
    console.rule("[bold bright_blue]⚙️  Configuration Files[/bold bright_blue]")

    if "error" in status:
        console.print(
            Panel(f"❌ Error reading configuration: {status['error']}", title="Configuration Files", border_style="red", padding=(1, 2), expand=False)
        )
        return

    public_percentage = (status["public_linked"] / status["public_count"] * 100) if status["public_count"] > 0 else 0
    private_percentage = (status["private_linked"] / status["private_count"] * 100) if status["private_count"] > 0 else 0

    table = Table(show_header=True, box=None, padding=(0, 2), expand=False)
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Linked", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Progress", justify="right")

    table.add_row("📂 Public", str(status["public_linked"]), str(status["public_count"]), f"{public_percentage:.0f}%")
    table.add_row("🔒 Private", str(status["private_linked"]), str(status["private_count"]), f"{private_percentage:.0f}%")

    overall_linked = status["public_linked"] + status["private_linked"]
    overall_total = status["public_count"] + status["private_count"]
    overall_percentage = (overall_linked / overall_total * 100) if overall_total > 0 else 0

    border_style = "green" if overall_percentage > 80 else ("yellow" if overall_percentage > 50 else "red")

    console.print(
        Panel(table, title=f"Configuration Files ({overall_percentage:.0f}% configured)", border_style=border_style, padding=(1, 2), expand=False)
    )


def _display_tools_status(grouped_tools: dict[str, dict[str, bool]]) -> None:
    """Display important tools installation status organized by groups."""
    console.rule("[bold bright_magenta]🛠️  Important Tools[/bold bright_magenta]")

    from rich.columns import Columns

    all_group_panels = []
    total_installed = 0
    total_tools = 0

    for group_name, tools in grouped_tools.items():
        sorted_tools = sorted(tools.keys())
        installed = [tool for tool, status in tools.items() if status]
        total_installed += len(installed)
        total_tools += len(tools)

        num_columns = 8
        tools_per_column = (len(sorted_tools) + num_columns - 1) // num_columns

        tables = []
        for col_idx in range(num_columns):
            table = Table(show_header=False, box=None, padding=(0, 0), collapse_padding=True)
            table.add_column("Tool", style="cyan", no_wrap=True, width=None)
            table.add_column("", justify="center", width=2, no_wrap=True)

            start_idx = col_idx * tools_per_column
            end_idx = min(start_idx + tools_per_column, len(sorted_tools))

            for i in range(start_idx, end_idx):
                tool = sorted_tools[i]
                status_icon = "✅" if tools[tool] else "❌"
                table.add_row(tool, status_icon)

            if start_idx < len(sorted_tools):
                tables.append(table)

        installed_percentage = (len(installed) / len(tools) * 100) if tools else 0
        border_style = "green" if installed_percentage > 80 else ("yellow" if installed_percentage > 50 else "red")

        group_display_name = group_name.replace("_", " ").title()
        group_panel = Panel(
            Columns(tables, equal=False, expand=False, padding=(0, 1)),
            title=f"{group_display_name} ({len(installed)}/{len(tools)})",
            border_style=border_style,
            padding=(0, 1),
            expand=False,
        )
        all_group_panels.append(group_panel)

    overall_percentage = (total_installed / total_tools * 100) if total_tools else 0
    master_border_style = "green" if overall_percentage > 80 else ("yellow" if overall_percentage > 50 else "red")

    from rich.console import Group

    master_panel = Panel(
        Group(*all_group_panels),
        title=f"🛠️  Tools Overview ({total_installed}/{total_tools} installed - {overall_percentage:.0f}%)",
        border_style=master_border_style,
        padding=(1, 2),
        expand=False,
    )
    console.print(master_panel)


def _display_backup_status(status: dict[str, Any]) -> None:
    """Display backup configuration status."""
    console.rule("[bold bright_cyan]💾 Backup Configuration[/bold bright_cyan]")

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("🌥️  Cloud Config", status["cloud_config"])
    table.add_row("📦 Backup Items", str(status["backup_items_count"]))

    border_style = "green" if status["cloud_config"] != "Not configured" else "yellow"

    console.print(Panel(table, title="Backup Configuration", border_style=border_style, padding=(1, 2), expand=False))


def main() -> None:
    """Main function to display comprehensive machine status."""
    console.print("\n")
    console.print(Panel(Text("📊 Machine Status Report", justify="center", style="bold white"), style="bold blue", padding=(1, 2)))
    console.print("\n")
    
    # system_info = _check_system_info()
    # from machineconfig.scripts.python.helpers_devops.devops_system_info import _check_system_info
    from machineconfig.scripts.python.helpers_utils.path import get_machine_specs
    system_info = get_machine_specs()
    from typing import cast
    system_info = cast(dict[str, str], system_info)
    _display_system_info(system_info)
    shell_status = _check_shell_profile_status()
    _display_shell_status(shell_status)

    repos_status = _check_repos_status()
    _display_repos_status(repos_status)

    ssh_status = _check_ssh_status()
    _display_ssh_status(ssh_status)

    config_status = _check_config_files_status()
    _display_config_files_status(config_status)

    tools_status = _check_important_tools()
    _display_tools_status(tools_status)

    backup_status = _check_backup_config()
    _display_backup_status(backup_status)

    console.print("\n")
    console.print(Panel(Text("✨ Status report complete!", justify="center", style="bold green"), style="green", padding=(1, 2)))
    console.print("\n")


if __name__ == "__main__":
    main()
