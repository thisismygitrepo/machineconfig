"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.

"""

from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text
from rich.table import Table

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.links import symlink_func, symlink_copy
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, REPO_ROOT
from machineconfig.profile.shell import create_default_shell_profile

import platform
import os
import ctypes
import subprocess
import tomllib
from typing import Optional, Any, TypedDict, Literal

system = platform.system()  # Linux or Windows
ERROR_LIST: list[Any] = []  # append to this after every exception captured.
SYSTEM = system.lower()

console = Console()


def get_other_systems(current_system: str) -> list[str]:
    all_systems = ["linux", "windows", "darwin"]
    return [s for s in all_systems if s != current_system.lower()]


OTHER_SYSTEMS = get_other_systems(SYSTEM)


class SymlinkMapper(TypedDict):
    this: str
    to_this: str
    contents: Optional[bool]


class OperationRecord(TypedDict):
    program: str
    file_key: str
    source: str
    target: str
    operation: str
    action: Literal[
        "already_linked",
        "relinking", 
        "fixing_broken_link",
        "identical_files",
        "backing_up_source",
        "backing_up_target", 
        "relinking_to_new_target",
        "moving_to_target",
        "new_link",
        "new_link_and_target",
        "linking",
        "copying",
        "error"
    ]
    details: str
    status: str


def apply_mapper(choice: Optional[str], prioritize_to_this: bool):
    symlink_mapper: dict[str, dict[str, SymlinkMapper]] = tomllib.loads(LIBRARY_ROOT.joinpath("profile/mapper.toml").read_text(encoding="utf-8"))
    exclude: list[str] = []  # "wsl_linux", "wsl_windows"
    operation_records: list[OperationRecord] = []

    program_keys_raw: list[str] = list(symlink_mapper.keys())
    program_keys: list[str] = []
    for program_key in program_keys_raw:
        if program_key in exclude or any([another_system in program_key for another_system in OTHER_SYSTEMS]):
            continue
        else:
            program_keys.append(program_key)

    program_keys.sort()
    if choice is None:
        choice_selected = choose_from_options(msg="Which symlink to create?", options=program_keys + ["all", "none(EXIT)"], default="none(EXIT)", fzf=True, multi=True)
        assert isinstance(choice_selected, list)
        if len(choice_selected) == 1 and choice_selected[0] == "none(EXIT)":
            return  # terminate function.
        elif len(choice_selected) == 1 and choice_selected[0] == "all":
            choice_selected = "all"  # i.e. program_keys = program_keys
    else:
        choice_selected = choice

    if isinstance(choice_selected, str):
        if str(choice_selected) == "all" and system == "Windows":
            if os.name == "nt":
                try:
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                except Exception:
                    is_admin = False
            else:
                is_admin = False
            if not is_admin:
                warning_body = "\n".join([
                    "[bold yellow]Administrator privileges required[/]",
                    "Run the terminal as admin and try again to avoid repeated elevation prompts.",
                ])
                console.print(
                    Panel.fit(
                        warning_body,
                        title="⚠️ Permission Needed",
                        border_style="yellow",
                        padding=(1, 2),
                    )
                )
                raise RuntimeError("Run terminal as admin and try again, otherwise, there will be too many popups for admin requests and no chance to terminate the program.")
        elif choice_selected == "all":
            console.print(
                Panel(
                    Pretty(program_keys),
                    title="🔍 Processing All Program Keys",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            pass  # i.e. program_keys = program_keys
        else:
            program_keys = [choice_selected]
    else:
        program_keys = choice_selected

    for program_key in program_keys:
        console.rule(f"🔄 Processing [bold]{program_key}[/] symlinks", style="cyan")
        for file_key, file_map in symlink_mapper[program_key].items():
            this = PathExtended(file_map["this"])
            to_this = PathExtended(file_map["to_this"].replace("REPO_ROOT", REPO_ROOT.as_posix()).replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()))
            
            if "contents" in file_map:
                try:
                    targets = list(to_this.expanduser().search("*"))
                    for a_target in targets:
                        result = symlink_func(this=this.joinpath(a_target.name), to_this=a_target, prioritize_to_this=prioritize_to_this)
                        operation_records.append({
                            "program": program_key,
                            "file_key": file_key,
                            "source": str(this.joinpath(a_target.name)),
                            "target": str(a_target),
                            "operation": "contents_symlink",
                            "action": result["action"],
                            "details": result["details"],
                            "status": "success"
                        })
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_key} | {file_key} | missing keys 'this ==> to_this'. {ex}")
                    operation_records.append({
                        "program": program_key,
                        "file_key": file_key,
                        "source": str(this),
                        "target": str(to_this),
                        "operation": "contents_symlink",
                        "action": "error",
                        "details": f"Failed to process contents: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })
                    
            elif "copy" in file_map:
                try:
                    result = symlink_copy(this=this, to_this=to_this, prioritize_to_this=prioritize_to_this)
                    operation_records.append({
                        "program": program_key,
                        "file_key": file_key,
                        "source": str(this),
                        "target": str(to_this),
                        "operation": "copy",
                        "action": result["action"],
                        "details": result["details"],
                        "status": "success"
                    })
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_key} | {file_key} | {ex}")
                    operation_records.append({
                        "program": program_key,
                        "file_key": file_key,
                        "source": str(this),
                        "target": str(to_this),
                        "operation": "copy",
                        "action": "error",
                        "details": f"Failed to copy: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })
            else:
                try:
                    result = symlink_func(this=this, to_this=to_this, prioritize_to_this=prioritize_to_this)
                    operation_records.append({
                        "program": program_key,
                        "file_key": file_key,
                        "source": str(this),
                        "target": str(to_this),
                        "operation": "symlink",
                        "action": result["action"],
                        "details": result["details"],
                        "status": "success"
                    })
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_key} | {file_key} | missing keys 'this ==> to_this'. {ex}")
                    operation_records.append({
                        "program": program_key,
                        "file_key": file_key,
                        "source": str(this),
                        "target": str(to_this),
                        "operation": "symlink",
                        "action": "error",
                        "details": f"Failed to create symlink: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })

            if program_key == "ssh" and system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
                try:
                    console.print("\n[bold]🔒 Setting secure permissions for SSH files...[/bold]")
                    subprocess.run("chmod 700 ~/.ssh/", check=True)
                    subprocess.run("chmod 700 ~/dotfiles/creds/.ssh/", check=True)  # may require sudo
                    subprocess.run("chmod 600 ~/dotfiles/creds/.ssh/*", check=True)
                    console.print("[green]✅ SSH permissions set successfully[/green]")
                except Exception as e:
                    ERROR_LIST.append(e)
                    console.print(f"❌ [red]Error setting SSH permissions[/red]: {e}")

    if system == "Linux":
        console.print("\n[bold]📜 Setting executable permissions for scripts...[/bold]")
        subprocess.run(f"chmod +x {LIBRARY_ROOT.joinpath(f'scripts/{system.lower()}')} -R", shell=True, capture_output=True, text=True)
        console.print("[green]✅ Script permissions updated[/green]")

    # Display operation summary table
    if operation_records:
        table = Table(title="🔗 Symlink Operations Summary", show_header=True, header_style="bold magenta")
        table.add_column("Program", style="cyan", no_wrap=True)
        table.add_column("File Key", style="blue", no_wrap=True)
        table.add_column("Source", style="green")
        table.add_column("Target", style="yellow")
        table.add_column("Operation", style="magenta", no_wrap=True)
        table.add_column("Action", style="red", no_wrap=True)
        table.add_column("Details", style="white")
        table.add_column("Status", style="red", no_wrap=True)
        
        for record in operation_records:
            status_style = "green" if record["status"] == "success" else "red"
            action_style = "green" if record["action"] != "error" else "red"
            table.add_row(
                record["program"],
                record["file_key"],
                record["source"],
                record["target"],
                record["operation"],
                f"[{action_style}]{record['action']}[/{action_style}]",
                record["details"],
                f"[{status_style}]{record['status']}[/{status_style}]"
            )
        
        console.print("\n")
        console.print(table)

    if len(ERROR_LIST) > 0:
        console.print(
            Panel(
                Pretty(ERROR_LIST),
                title="❗ Errors Encountered During Processing",
                border_style="red",
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel.fit(
                Text("✅ All symlinks created successfully!", justify="center"),
                title="Symlink Creation Complete",
                border_style="green",
            )
        )


def main_symlinks():
    console.print("")
    console.rule("[bold blue]🔗 CREATING SYMLINKS 🔗")
    apply_mapper(choice="all", prioritize_to_this=True)


def main_profile():
    console.print("")
    console.rule("[bold green]🐚 CREATING SHELL PROFILE 🐚")
    create_default_shell_profile()
    console.print(
        Panel.fit(
            Text("✨ Configuration setup complete! ✨", justify="center"),
            title="Profile Setup",
            border_style="green",
        )
    )


if __name__ == "__main__":
    pass
