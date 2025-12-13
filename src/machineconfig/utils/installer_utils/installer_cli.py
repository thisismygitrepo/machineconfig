
"""Devops Devapps Install
"""

from machineconfig.utils.installer_utils.installer_helper import get_group_name_to_repr
import typer
from typing import Annotated, Optional


def main_installer_cli(
    which: Annotated[Optional[str], typer.Argument(..., help="Comma-separated list of program/groups names to install (if --group flag is set).")] = None,
    group: Annotated[bool, typer.Option(..., "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps.")] = False,
    interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of programs to install.")] = False,
) -> None:
    if interactive:
        return install_interactively()
    if which is not None:
        if group:
            for a_group in [x.strip() for x in which.split(",") if x.strip() != ""]:
                return install_group(package_group=a_group)
        else:
            return install_clis(clis_names=[x.strip() for x in which.split(",") if x.strip() != ""])
    else:
        if group:
            from rich.console import Console
            from rich.table import Table
            console = Console()

            typer.echo("❌ You must provide a group name when using the --group/-g option.")
            from machineconfig.utils.installer_utils.installer_helper import get_group_name_to_repr
            res = get_group_name_to_repr()
            console.print("[bold blue]Here are the available groups:[/bold blue]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Group", style="cyan", no_wrap=True)
            table.add_column("AppsBundled", style="green", overflow="fold")
            for display, group_name in res.items():
                # Parse display
                if "   --   " in display:
                    group_part, items_part = display.split("   --   ", 1)
                    group_name_parsed = group_part.replace("📦 ", "").strip()
                    items_str = items_part.strip()
                else:
                    group_name_parsed = display
                    items_str = group_name
                table.add_row(group_name_parsed, items_str)
            console.print(table)
            raise typer.Exit(1)
    typer.echo("❌ You must provide either a program name/group name, or use --interactive/-ia option.")
    import click
    ctx = click.get_current_context()
    typer.echo(ctx.get_help())
    raise typer.Exit(1)





def install_interactively():
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer_utils.installer_runner import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    from rich.console import Console
    from rich.panel import Panel
    # from rich.table import Table
    installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=None)
    installer_options = [Installer(installer_data=x).get_description() for x in installers]
    category_display_to_name = get_group_name_to_repr()
    options = list(category_display_to_name.keys()) + installer_options
    program_names = choose_from_options(multi=True, msg="Categories are prefixed with 📦", options=options, header="🚀 CHOOSE DEV APP OR CATEGORY", tv=True)
    installation_messages: list[str] = []
    for _an_idx, a_program_name in enumerate(program_names):
        if a_program_name.startswith("📦 "):
            category_name = category_display_to_name.get(a_program_name)
            if category_name:
                install_group(package_group=category_name)
        else:
            installer_idx = installer_options.index(a_program_name)
            an_installer_data = installers[installer_idx]
            status_message = Installer(an_installer_data).install_robust(version=None)  # finish the task - this returns a status message, not a command
            installation_messages.append(status_message)
    if installation_messages:
        console = Console()

        panel = Panel("\n".join([f"[blue]• {message}[/blue]" for message in installation_messages]), title="[bold green]📊 Installation Summary[/bold green]", border_style="green", padding=(1, 2))
        console.print(panel)


def install_group(package_group: str):
    from machineconfig.utils.installer_utils.installer_runner import get_installers, install_bulk
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from rich.console import Console
    from rich.panel import Panel
    # from rich.table import Table
    from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES
    if package_group in PACKAGE_GROUP2NAMES:
        panel = Panel(f"[bold yellow]Installing programs from category: [green]{package_group}[/green][/bold yellow]", title="[bold blue]📦 Category Installation[/bold blue]", border_style="blue", padding=(1, 2))
        console = Console()
        console.print(panel)
        installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=[package_group])
        install_bulk(installers_data=installers_)
        return
    console = Console()
    console.print(f"❌ ERROR: Unknown package group: {package_group}. Available groups are: {list(PACKAGE_GROUP2NAMES.keys())}")


def install_clis(clis_names: list[str]):
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer_utils.installer_runner import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    from rich.console import Console
    all_installers_data = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=None)
    total_messages: list[str] = []
    for a_cli_name in clis_names:
        if "github.com" in a_cli_name.lower():
            from machineconfig.utils.installer_utils.install_from_url import install_from_github_url
            install_from_github_url(github_url=a_cli_name)
            continue
        elif a_cli_name.startswith("https://") or a_cli_name.startswith("http://"):
            print(f"⏳ Installing from binary URL: {a_cli_name} ...")
            from machineconfig.utils.installer_utils.install_from_url import install_from_binary_url
            install_from_binary_url(binary_url=a_cli_name)
            continue
        selected_installer = None
        for installer in all_installers_data:
            app_name = installer["appName"]
            if app_name.lower() == a_cli_name.lower():
                selected_installer = installer
                break
        if selected_installer is None:
            from machineconfig.utils.installer_utils.installer_helper import handle_installer_not_found
            handle_installer_not_found(a_cli_name, all_installers_data)
            return None
        message = Installer(selected_installer).install_robust(version=None)  # finish the task
        total_messages.append(message)
    if total_messages:
        console = Console()
        console.print("\n[bold green]📊 Installation Results:[/bold green]")
        for a_message in total_messages:
            console.print(f"[blue]• {a_message}[/blue]")
    return None
def install_if_missing(which: str) -> bool:
    from machineconfig.utils.installer_utils.installer_locator_utils import check_tool_exists
    exists = check_tool_exists(which)
    if exists:
        print(f"✅ {which} is already installed.")
        return True
    print(f"⏳ {which} not found. Installing...")
    from machineconfig.utils.installer_utils.installer_cli import main_installer_cli
    try:
        main_installer_cli(which=which, interactive=False)
        return True
    except Exception as e:
        print(f"❌ Error installing {which}: {e}")
    return False

if __name__ == "__main__":
    from machineconfig.utils.schemas.installer.installer_types import InstallerData
    from machineconfig.utils.installer_utils.installer_class import Installer
    _ = InstallerData, Installer
    pass
