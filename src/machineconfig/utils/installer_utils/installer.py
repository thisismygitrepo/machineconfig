"""Devops Devapps Install"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional, Annotated
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUP2NAMES

console = Console()


def _handle_installer_not_found(search_term: str, all_names: list[str]) -> None:  # type: ignore
    """Handle installer not found with friendly suggestions using fuzzy matching."""
    from difflib import get_close_matches
    close_matches = get_close_matches(search_term, all_names, n=5, cutoff=0.4)
    console.print(f"\n❌ '[red]{search_term}[/red]' was not found.", style="bold")
    if close_matches:
        console.print("🤔 Did you mean one of these?", style="yellow")
        table = Table(show_header=False, box=None, pad_edge=False)
        for i, match in enumerate(close_matches, 1):
            table.add_row(f"[cyan]{i}.[/cyan]", f"[green]{match}[/green]")
        console.print(table)
    else:
        console.print("📋 Here are some available options:", style="blue")
        # Show first 10 installers as examples
        if len(all_names) > 10:
            sample_names = all_names[:10]
        else:
            sample_names = all_names
        table = Table(show_header=False, box=None, pad_edge=False)
        for i, name in enumerate(sample_names, 1):
            table.add_row(f"[cyan]{i}.[/cyan]", f"[green]{name}[/green]")
        console.print(table)
        if len(all_names) > 10:
            console.print(f"   [dim]... and {len(all_names) - 10} more[/dim]")

    panel = Panel(f"[bold blue]💡 Use 'ia' to interactively browse all available installers.[/bold blue]\n[bold blue]💡 Use one of the categories: {list(PACKAGE_GROUP2NAMES.keys())}[/bold blue]", title="[yellow]Helpful Tips[/yellow]", border_style="yellow")
    console.print(panel)


def main_with_parser():
    import typer
    app = typer.Typer()
    app.command()(main)
    app()


def main(
    which: Annotated[Optional[str], typer.Argument(..., help="Comma-separated list of program/groups names to install (if --group flag is set).")] = None,
    group: Annotated[bool, typer.Option(..., "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps.")] = False,
    interactive: Annotated[bool, typer.Option(..., "--interactive", "-ia", help="Interactive selection of programs to install.")] = False,
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
            typer.echo("❌ You must provide a group name when using the --group/-g option.")
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


def get_group_name_to_repr() -> dict[str, str]:
    # Build category options and maintain a mapping from display text to actual category name
    category_display_to_name: dict[str, str] = {}
    for group_name, group_values in PACKAGE_GROUP2NAMES.items():
        display = f"📦 {group_name:<20}" + "   --   " + f"{'|'.join(group_values):<60}"
        category_display_to_name[display] = group_name
    return category_display_to_name


def install_interactively():
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=None)
    installer_options = []
    for x in installers:
        installer_options.append(Installer(installer_data=x).get_description())

    category_display_to_name = get_group_name_to_repr()
    options = list(category_display_to_name.keys()) + ["─" * 50] + installer_options
    program_names = choose_from_options(multi=True, msg="Categories are prefixed with 📦", options=options, header="🚀 CHOOSE DEV APP OR CATEGORY", default="📦 termabc", fzf=True)
    installation_messages: list[str] = []
    for _an_idx, a_program_name in enumerate(program_names):
        if a_program_name.startswith("─"):  # 50 dashes separator
            continue
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
        panel = Panel("\n".join([f"[blue]• {message}[/blue]" for message in installation_messages]), title="[bold green]📊 Installation Summary[/bold green]", border_style="green", padding=(1, 2))
        console.print(panel)


def install_group(package_group: str):
    from machineconfig.utils.installer import get_installers, install_bulk
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    if package_group in PACKAGE_GROUP2NAMES:
        panel = Panel(f"[bold yellow]Installing programs from category: [green]{package_group}[/green][/bold yellow]", title="[bold blue]📦 Category Installation[/bold blue]", border_style="blue", padding=(1, 2))
        console.print(panel)
        installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=[package_group])
        install_bulk(installers_data=installers_)
        return
    print(f"❌ ERROR: Unknown package group: {package_group}. Available groups are: {list(PACKAGE_GROUP2NAMES.keys())}")
def install_clis(clis_names: list[str]):
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    total_messages: list[str] = []
    for a_which in clis_names:
        all_installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=None)
        selected_installer = None
        for installer in all_installers:
            app_name = installer["appName"]
            if app_name.lower() == a_which.lower():
                selected_installer = installer
                break
        if selected_installer is None:
            _handle_installer_not_found(a_which, all_names=[inst["appName"] for inst in all_installers])
            return None
        message = Installer(selected_installer).install_robust(version=None)  # finish the task
        total_messages.append(message)
    if total_messages:
        console.print("\n[bold green]📊 Installation Results:[/bold green]")
        for a_message in total_messages:
            console.print(f"[blue]• {a_message}[/blue]")
    return None


def install_if_missing(which: str):
    from machineconfig.utils.installer_utils.installer_abc import check_tool_exists
    exists = check_tool_exists(which)
    if exists:
        print(f"✅ {which} is already installed.")
        return
    print(f"⏳ {which} not found. Installing...")
    from machineconfig.utils.installer_utils.installer import main
    main(which=which, interactive=False)


if __name__ == "__main__":
    from machineconfig.utils.schemas.installer.installer_types import InstallerData
    from machineconfig.utils.installer_utils.installer_class import Installer

    _ = InstallerData, Installer
    pass
