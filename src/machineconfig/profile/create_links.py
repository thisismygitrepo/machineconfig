"""
This script Takes away all config files from the computer, place them in one directory
`dotfiles`, and create symlinks to those files from thier original locations.

"""

from machineconfig.utils.links import OperationRecord
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text
from rich.table import Table

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.links import symlink_map, copy_map
from machineconfig.profile.create_links_export import ON_CONFLICT_STRICT
from machineconfig.utils.source_of_truth import LIBRARY_ROOT, CONFIG_ROOT

import platform
import subprocess
import tomllib
from typing import Optional, Any, TypedDict, Literal


system = platform.system()  # Linux or Windows
ERROR_LIST: list[Any] = []  # append to this after every exception captured.
SYSTEM = system.lower()

console = Console()


class Base(TypedDict):
    original: str
    self_managed: str
    contents: Optional[bool]
    copy: Optional[bool]
class ConfigMapper(TypedDict):
    file_name: str
    config_file_default_path: str
    self_managed_config_file_path: str
    contents: Optional[bool]
    copy: Optional[bool]
class MapperFileData(TypedDict):
    public: dict[str, list[ConfigMapper]]
    private: dict[str, list[ConfigMapper]]
def read_mapper() -> MapperFileData:
    mapper_data: dict[str, dict[str, Base]] = tomllib.loads(LIBRARY_ROOT.joinpath("profile/mapper.toml").read_text(encoding="utf-8"))
    public: dict[str, list[ConfigMapper]] = {}
    private: dict[str, list[ConfigMapper]] = {}
    # def get_other_systems(current_system: str) -> list[str]:
    #     all_systems = ["linux", "windows", "darwin"]
    #     return [s for s in all_systems if s != current_system.lower()]
    # OTHER_SYSTEMS = get_other_systems(SYSTEM)
    for program_key, program_map in mapper_data.items():
        parts = program_key.split("_")
        if len(parts) > 1:
            if parts[-1].lower() == "windows" and SYSTEM != "windows":
                # console.print(f"Skipping Windows-only program mapping: {program_key}")
                continue
            elif parts[-1].lower() == "linux" and SYSTEM == "windows":
                # console.print(f"Skipping Linux-only program mapping: {program_key}")
                continue
        for file_name, file_base in program_map.items():
            file_map: ConfigMapper = {
                "file_name": file_name,
                "config_file_default_path": file_base["original"],
                "self_managed_config_file_path": file_base["self_managed"],
                "contents": file_base.get("contents"),
                "copy": file_base.get("copy"),
            }
            if "CONFIG_ROOT" in file_map["self_managed_config_file_path"]:
                if program_key not in public:
                    public[program_key] = []
                public[program_key].append(file_map)
            else:
                if program_key not in private:
                    private[program_key] = []
                private[program_key].append(file_map)
    return {"public": public, "private": private}


def apply_mapper(mapper_data: dict[str, list[ConfigMapper]],
                 on_conflict: ON_CONFLICT_STRICT,
                 method: Literal["symlink", "copy"]
                 ):
    operation_records: list[OperationRecord] = []
    print(f"Working with {len(mapper_data)} programs from mapper data.")
    if len(mapper_data) == 1:
        print(mapper_data)
    import os
    if os.name == "nt":
        import ctypes
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            is_admin = False
        total_length = sum(len(item) for item in mapper_data.values())
        if not is_admin and method == "symlink" and total_length > 5:
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
    for program_name, program_files in mapper_data.items():
        console.rule(f"🔄 Processing [bold]{program_name}[/] symlinks", style="cyan")
        for a_mapper in program_files:
            config_file_default_path = PathExtended(a_mapper["config_file_default_path"])
            self_managed_config_file_path = PathExtended(a_mapper["self_managed_config_file_path"].replace("CONFIG_ROOT", CONFIG_ROOT.as_posix()))
            # Determine whether to use copy or symlink
            use_copy = method == "copy" or a_mapper.get("copy", False)
            if "contents" in a_mapper and a_mapper["contents"]:
                targets = list(self_managed_config_file_path.expanduser().glob("*"))
                for a_target in targets:
                    operation_type = "contents_copy" if use_copy else "contents_symlink"
                    try:
                        if use_copy:
                            result = copy_map(config_file_default_path=config_file_default_path.joinpath(a_target.name), self_managed_config_file_path=a_target, on_conflict=on_conflict)
                        else:
                            result = symlink_map(config_file_default_path=config_file_default_path.joinpath(a_target.name), self_managed_config_file_path=a_target, on_conflict=on_conflict)
                        operation_records.append({
                            "program": program_name,
                            "file_key": a_mapper["file_name"],
                            "defaultPath": str(config_file_default_path.joinpath(a_target.name)),
                            "selfManaged": str(a_target),
                            "operation": operation_type,
                            "action": result["action"],
                            "details": result["details"],
                            "status": "success"
                        })
                    except ValueError as ex:
                        if "resolve to the same location" in str(ex):
                            operation_records.append({
                                "program": program_name,
                                "file_key": a_mapper["file_name"],
                                "defaultPath": str(config_file_default_path.joinpath(a_target.name)),
                                "selfManaged": str(a_target),
                                "operation": operation_type,
                                "action": "already_linked",
                                "details": "defaultPath and selfManaged resolve to same location - already correctly configured",
                                "status": "success"
                            })
                        else:
                            raise
                    except Exception as ex:
                        console.print(f"❌ [red]Config error[/red]: {program_name} | {a_mapper['file_name']} | {a_target.name}. {ex}")
                        operation_records.append({
                            "program": program_name,
                            "file_key": a_mapper["file_name"],
                            "defaultPath": str(config_file_default_path.joinpath(a_target.name)),
                            "selfManaged": str(a_target),
                            "operation": operation_type,
                            "action": "error",
                            "details": f"Failed to process contents: {str(ex)}",
                            "status": f"error: {str(ex)}"
                        })                    
            else:
                operation_type = "copy" if use_copy else "symlink"
                try:
                    if use_copy:
                        result = copy_map(config_file_default_path=config_file_default_path, self_managed_config_file_path=self_managed_config_file_path, on_conflict=on_conflict)
                    else:
                        result = symlink_map(config_file_default_path=config_file_default_path, self_managed_config_file_path=self_managed_config_file_path, on_conflict=on_conflict)
                    operation_records.append({
                        "program": program_name,
                        "file_key": a_mapper["file_name"],
                        "defaultPath": str(config_file_default_path),
                        "selfManaged": str(self_managed_config_file_path),
                        "operation": operation_type,
                        "action": result["action"],
                        "details": result["details"],
                        "status": "success"
                    })
                except ValueError as ex:
                    if "resolve to the same location" in str(ex):
                        operation_records.append({
                            "program": program_name,
                            "file_key": a_mapper["file_name"],
                            "defaultPath": str(config_file_default_path),
                            "selfManaged": str(self_managed_config_file_path),
                            "operation": operation_type,
                            "action": "already_linked",
                            "details": "defaultPath and selfManaged resolve to same location - already correctly configured",
                            "status": "success"
                        })
                    else:
                        raise
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_name} | {a_mapper['file_name']} | {ex}")
                    operation_records.append({
                        "program": program_name,
                        "file_key": a_mapper["file_name"],
                        "defaultPath": str(config_file_default_path),
                        "selfManaged": str(self_managed_config_file_path),
                        "operation": operation_type,
                        "action": "error",
                        "details": f"Failed to create {operation_type}: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })

            if program_name == "ssh" and system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
                try:
                    console.print("\n[bold]🔒 Setting secure permissions for SSH files...[/bold]")
                    subprocess.run("chmod 700 $HOME/.ssh/", shell=True, check=True)
                    subprocess.run("chmod 700 $HOME/dotfiles/creds/.ssh/", shell=True, check=True)
                    subprocess.run("chmod 600 $HOME/dotfiles/creds/.ssh/*", shell=True, check=True)
                    subprocess.run("chmod 600 $HOME/.ssh/*", shell=True, check=True)
                    console.print("[green]✅ SSH permissions set successfully[/green]")
                except Exception as e:
                    ERROR_LIST.append(e)
                    console.print(f"❌ [red]Error setting SSH permissions[/red]: {e}")

    # Display operation summary table
    if operation_records:
        table = Table(title="🔗 Symlink Operations Summary", show_header=True, header_style="bold magenta")
        table.add_column("Program", style="cyan", no_wrap=True)
        table.add_column("File Key", style="blue", no_wrap=True)
        table.add_column("Default Path", style="green")
        table.add_column("Self Managed", style="yellow")
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
                record["defaultPath"],
                record["selfManaged"],
                record["operation"],
                f"[{action_style}]{record['action']}[/{action_style}]",
                record["details"],
                f"[{status_style}]{record['status']}[/{status_style}]"
            )
        
        console.print("\n")
        console.print(table)
        
        # Export operation records to CSV
        import csv
        from datetime import datetime

        csv_dir = PathExtended(CONFIG_ROOT).joinpath("symlink_operations")
        csv_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"symlink_operations_{timestamp}.csv"
        csv_path = csv_dir.joinpath(csv_filename)
        
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["program", "file_key", "defaultPath", "selfManaged", "operation", "action", "details", "status"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(operation_records)
        
        console.print(f"\n[bold green]📊 Operations exported to CSV:[/bold green] [cyan]{csv_path}[/cyan]")

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


if __name__ == "__main__":
    pass
