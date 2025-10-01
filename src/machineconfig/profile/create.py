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
from machineconfig.utils.links import symlink_map, copy_map
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

import platform
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


class Base(TypedDict):
    this: str
    to_this: str
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
    for program_key, program_map in mapper_data.items():
        for file_name, file_base in program_map.items():
            file_map: ConfigMapper = {
                "file_name": file_name,
                "config_file_default_path": file_base["this"],
                "self_managed_config_file_path": file_base["to_this"],
                "contents": file_base.get("contents"),
                "copy": file_base.get("copy"),
            }
            if "LIBRARY_ROOT" in file_map["self_managed_config_file_path"]:
                if program_key not in public:
                    public[program_key] = []
                public[program_key].append(file_map)
            else:
                if program_key not in private:
                    private[program_key] = []
                private[program_key].append(file_map)
    return {"public": public, "private": private}


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


def apply_mapper(mapper_data: dict[str, list[ConfigMapper]],
                 on_conflict: Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"],
                 method: Literal["symlink", "copy"]
                 ):
    operation_records: list[OperationRecord] = []

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
            self_managed_config_file_path = PathExtended(a_mapper["self_managed_config_file_path"].replace("LIBRARY_ROOT", LIBRARY_ROOT.as_posix()))
            
            # Determine whether to use copy or symlink
            use_copy = method == "copy" or "copy" in a_mapper
            
            if "contents" in a_mapper:
                try:
                    targets = list(self_managed_config_file_path.expanduser().search("*"))
                    for a_target in targets:
                        if use_copy:
                            result = copy_map(config_file_default_path=config_file_default_path.joinpath(a_target.name), self_managed_config_file_path=a_target, on_conflict=on_conflict)
                            operation_type = "contents_copy"
                        else:
                            result = symlink_map(config_file_default_path=config_file_default_path.joinpath(a_target.name), self_managed_config_file_path=a_target, on_conflict=on_conflict)
                            operation_type = "contents_symlink"
                        operation_records.append({
                            "program": program_name,
                            "file_key": a_mapper["file_name"],
                            "source": str(config_file_default_path.joinpath(a_target.name)),
                            "target": str(a_target),
                            "operation": operation_type,
                            "action": result["action"],
                            "details": result["details"],
                            "status": "success"
                        })
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_name} | {a_mapper['file_name']} | missing keys 'config_file_default_path ==> self_managed_config_file_path'. {ex}")
                    operation_records.append({
                        "program": program_name,
                        "file_key": a_mapper["file_name"],
                        "source": str(config_file_default_path),
                        "target": str(self_managed_config_file_path),
                        "operation": "contents_symlink" if not use_copy else "contents_copy",
                        "action": "error",
                        "details": f"Failed to process contents: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })                    
            else:
                try:
                    if use_copy:
                        result = copy_map(config_file_default_path=config_file_default_path, self_managed_config_file_path=self_managed_config_file_path, on_conflict=on_conflict)
                        operation_type = "copy"
                    else:
                        result = symlink_map(config_file_default_path=config_file_default_path, self_managed_config_file_path=self_managed_config_file_path, on_conflict=on_conflict)
                        operation_type = "symlink"
                    operation_records.append({
                        "program": program_name,
                        "file_key": a_mapper["file_name"],
                        "source": str(config_file_default_path),
                        "target": str(self_managed_config_file_path),
                        "operation": operation_type,
                        "action": result["action"],
                        "details": result["details"],
                        "status": "success"
                    })
                except Exception as ex:
                    console.print(f"❌ [red]Config error[/red]: {program_name} | {a_mapper['file_name']} | missing keys 'config_file_default_path ==> self_managed_config_file_path'. {ex}")
                    operation_records.append({
                        "program": program_name,
                        "file_key": a_mapper["file_name"],
                        "source": str(config_file_default_path),
                        "target": str(self_managed_config_file_path),
                        "operation": "symlink" if not use_copy else "copy",
                        "action": "error",
                        "details": f"Failed to create {'symlink' if not use_copy else 'copy'}: {str(ex)}",
                        "status": f"error: {str(ex)}"
                    })

            if program_name == "ssh" and system == "Linux":  # permissions of ~/dotfiles/.ssh should be adjusted
                try:
                    console.print("\n[bold]🔒 Setting secure permissions for SSH files...[/bold]")
                    # run_shell_script("sudo chmod 600 $HOME/.ssh/*")
                    # run_shell_script("sudo chmod 700 $HOME/.ssh")

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


if __name__ == "__main__":
    pass
