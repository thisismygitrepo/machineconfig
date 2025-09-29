"""Devops Devapps Install"""

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from platform import system
from typing import Optional, Literal, TypeAlias, cast, get_args, Annotated

console = Console()

WHICH_CAT: TypeAlias = Literal["essentials", "essentialsDev", "systemPackages", "precheckedPackages", "ia"]


def _handle_installer_not_found(search_term: str, all_installers: list["InstallerData"]) -> None:  # type: ignore
    """Handle installer not found with friendly suggestions using fuzzy matching."""
    from difflib import get_close_matches
    
    # Get all possible names (both exe names and app names)
    all_names = []
    for inst in all_installers:
        exe_name = inst["appName"]
        all_names.append(exe_name)
    
    # Find close matches using fuzzy matching
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
        sample_names = []
        for inst in all_installers[:10]:
            exe_name = inst["appName"]
            sample_names.append(exe_name)        
        
        table = Table(show_header=False, box=None, pad_edge=False)
        for i, name in enumerate(sample_names, 1):
            table.add_row(f"[cyan]{i}.[/cyan]", f"[green]{name}[/green]")
        console.print(table)
        
        if len(all_installers) > 10:
            console.print(f"   [dim]... and {len(all_installers) - 10} more[/dim]")
    
    panel = Panel(
        "[bold blue]💡 Use 'ia' to interactively browse all available installers.[/bold blue]\n"
        f"[bold blue]💡 Use one of the categories: {list(get_args(WHICH_CAT))}[/bold blue]",
        title="[yellow]Helpful Tips[/yellow]",
        border_style="yellow"
    )
    console.print(panel)


def main_with_parser():
    import typer
    app = typer.Typer()
    app.command()(main)
    app()


def main(which: Annotated[Optional[str], typer.Argument(help=f"Choose a category or program to install, {list(get_args(WHICH_CAT))} or <program_name> or list of programs names separated by comma.")]) -> None:
    if which in get_args(WHICH_CAT):  # install by category
        return get_programs_by_category(program_name=which)  # type: ignore
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    if which != "ia" and which is not None:  # install by name
        total_messages: list[str] = []
        for a_which in which.split(",") if type(which) == str else which:
            all_installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["ESSENTIAL", "DEV"])

            # Find installer by exe_name or name
            selected_installer = None
            for installer in all_installers:
                exe_name = installer["appName"]
                app_name = installer["appName"]
                if exe_name == a_which or app_name == a_which:
                    selected_installer = installer
                    break

            if selected_installer is None:
                _handle_installer_not_found(a_which, all_installers)
                return None
            message = Installer(selected_installer).install_robust(version=None)  # finish the task
            total_messages.append(message)
        
        if total_messages:
            console.print("\n[bold green]📊 Installation Results:[/bold green]")
            for a_message in total_messages:
                console.print(f"[blue]• {a_message}[/blue]")
        return None



def install_interactively():
    from machineconfig.utils.options import choose_from_options
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.installer import get_installers
    from machineconfig.utils.installer_utils.installer_class import Installer
    installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["ESSENTIAL", "DEV"])
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("✅ Checking installed programs...", total=len(installers))
        installer_options = []
        for x in installers:
            installer_options.append(Installer(installer_data=x).get_description())
            progress.update(task, advance=1)
    category_options = [f"📦 {cat}" for cat in get_args(WHICH_CAT)]
    options = category_options + ["─" * 50] + installer_options    
    program_names = choose_from_options(multi=True, msg="Categories are prefixed with 📦", options=options, header="🚀 CHOOSE DEV APP OR CATEGORY", default="📦 essentials", fzf=True)
    installation_messages: list[str] = []
    for _an_idx, a_program_name in enumerate(program_names):
        if a_program_name.startswith("─"):
            continue
        if a_program_name.startswith("📦 "):
            category_name = a_program_name[2:]  # Remove "📦 " prefix
            if category_name in get_args(WHICH_CAT):
                get_programs_by_category(program_name=cast(WHICH_CAT, category_name))
        else:
            installer_idx = installer_options.index(a_program_name)
            an_installer_data = installers[installer_idx]
            status_message = Installer(an_installer_data).install_robust(version=None)  # finish the task - this returns a status message, not a command
            installation_messages.append(status_message)
    if installation_messages:
        panel = Panel(
            "\n".join([f"[blue]• {message}[/blue]" for message in installation_messages]),
            title="[bold green]📊 Installation Summary[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)


def get_programs_by_category(program_name: WHICH_CAT):
    panel = Panel(
        f"[bold yellow]Installing programs from category: [green]{program_name}[/green][/bold yellow]",
        title="[bold blue]📦 Category Installation[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    from machineconfig.utils.source_of_truth import LIBRARY_ROOT
    from machineconfig.utils.installer import get_installers, install_all
    from machineconfig.utils.installer_utils.installer_abc import parse_apps_installer_linux, parse_apps_installer_windows
    from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
    from machineconfig.utils.options import choose_from_options
    match program_name:
        case "essentials":
            installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["ESSENTIAL"])
            install_all(installers_data=installers_)
        case "essentialsDev":
            installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["DEV", "ESSENTIAL"])
            install_all(installers_data=installers_)
        case "systemPackages":
            if system() == "Windows":
                options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text(encoding="utf-8"))
            elif system() == "Linux":
                options_system = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text(encoding="utf-8"))
            else:
                raise NotImplementedError(f"❌ System {system()} not supported")
            
            # Create display options that include descriptions for user selection
            display_options = []
            for group_name, (description, _) in options_system.items():
                if description:
                    display_options.append(f"{group_name:<20} - {description}")
                else:
                    display_options.append(group_name)
            
            program_names = choose_from_options(multi=True, msg="", options=sorted(display_options), header="🚀 CHOOSE DEV APP", fzf=True)
            program = ""
            for display_name in program_names:
                # Extract the actual group name (everything before " - " if present)
                group_name = display_name.split(" - ")[0].strip() if " - " in display_name else display_name.strip()
                
                console.print(f"\n[bold cyan]⚙️  Installing: [yellow]{group_name}[/yellow][/bold cyan]", style="bold")
                
                _, sub_program = options_system[group_name]  # Extract content from tuple
                if sub_program.startswith("#winget"):
                    sub_program = sub_program[1:]
                program += "\n" + sub_program
            from pathlib import Path
            if system() == "Windows":
                temp_script_path = Path("C:/Windows/Temp/temp_install_script.ps1")
                lexer = "powershell"
            else:
                temp_script_path = Path("/tmp/temp_install_script.sh")
                lexer = "bash"
            temp_script_path.write_text(program, encoding="utf-8")
            console.print(f"📝 [blue]Temporary script written to:[/blue] [green]{temp_script_path}[/green]")
            from rich.syntax import Syntax
            console.print(Panel(Syntax(code=program, lexer=lexer), title="📄 Installation Program", subtitle="shell code"), style="bold red")
            console.print("🚀 [bold yellow]Starting installation...[/bold yellow]")
            if system() == "Windows":
                import subprocess
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(temp_script_path)], check=True)
            elif system() == "Linux":
                import subprocess
                subprocess.run(["bash", str(temp_script_path)], check=True)
            console.print("✅ [bold green]Installation completed.[/bold green]")
            temp_script_path.unlink(missing_ok=True)
        case "ia":
            install_interactively()
        case "precheckedPackages":
            # from machineconfig.jobs.python.check_installations import precheckedPackages
            # ci = precheckedPackages()
            # ci.download_safe_apps(name="essentials")
            # program = ""
            raise NotImplementedError("precheckedPackages is not implemented yet.")


if __name__ == "__main__":
    from machineconfig.utils.schemas.installer.installer_types import InstallerData
    from machineconfig.utils.installer_utils.installer_class import Installer
    _ = InstallerData, Installer
    pass
