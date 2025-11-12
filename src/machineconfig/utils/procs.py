"""Procs"""

import psutil
from rich.progress import Progress, SpinnerColumn, TextColumn
from machineconfig.utils.options import choose_from_options
from typing import Optional, TypedDict, List, Dict
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
from machineconfig.utils.accessories import pprint

console = Console()

BOX_WIDTH = 78  # width for box drawing


class ProcessInfo(TypedDict):
    """TypedDict for process information."""
    command: str
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_usage_mb: float
    status: str
    create_time: datetime


class FileAccessInfo(TypedDict):
    """TypedDict for file access information."""
    pid: int
    files: List[str]


def get_processes_accessing_file(path: str) -> List[FileAccessInfo]:
    # header for searching processes
    title = "🔍  SEARCHING FOR PROCESSES ACCESSING FILE"
    console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
    res: Dict[int, List[str]] = {}

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task("🔎 Scanning processes...", total=None)

        for proc in psutil.process_iter():
            try:
                files = proc.open_files()
            except psutil.AccessDenied:
                continue
            tmp = [file.path for file in files if path in file.path]
            if len(tmp) > 0:
                res[proc.pid] = tmp

    # Convert to list of dictionaries for consistent data structure
    result_data: List[FileAccessInfo] = [{"pid": pid, "files": files} for pid, files in res.items()]
    console.print(Panel(f"✅ Found {len(res)} processes accessing the specified file", title="[bold blue]Process Info[/bold blue]", border_style="blue"))
    return result_data


def kill_process(name: str):
    console.print(f"⚠️  Attempting to kill process: {name}...", style="yellow")
    killed = False
    for proc in psutil.process_iter():
        if proc.name() == name:
            proc.kill()
            console.print(f"💀 Process {name} (PID: {proc.pid}) terminated successfully", style="green")
            killed = True
    if not killed:
        console.print(f"❓ No process with name '{name}' was found", style="red")
    console.rule(style="dim")


class ProcessManager:
    def __init__(self):
        # header for initializing process manager
        title = "📊  INITIALIZING PROCESS MANAGER"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
        process_info: List[ProcessInfo] = []
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("🔍 Reading system processes...", total=None)
            for proc in psutil.process_iter():
                try:
                    mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
                    create_time = datetime.fromtimestamp(proc.create_time(), tz=None)

                    process_info.append(
                        {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "username": proc.username(),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_usage_mb": mem_usage_mb,
                            "status": proc.status(),
                            "create_time": create_time,
                            "command": " ".join(proc.cmdline()),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

        # Sort by memory usage (descending)
        process_info.sort(key=lambda x: x["memory_usage_mb"], reverse=True)
        self.data = process_info
        console.print(Panel(f"✅ Process Manager initialized with {len(process_info)} processes", title="[bold blue]Process Info[/bold blue]", border_style="blue"))

    def _format_process_table(self) -> str:
        """Format process data as table string for display."""
        if not self.data:
            return ""
        # Create header
        _headers = ["Command", "PID", "Name", "Username", "CPU%", "Memory(MB)", "Status", "Create Time"]
        header_line = f"{'Command':<50} {'PID':<8} {'Name':<20} {'Username':<12} {'CPU%':<8} {'Memory(MB)':<12} {'Status':<12} {'Create Time':<20}"
        separator = "-" * len(header_line)
        lines = [header_line, separator]
        for process in self.data:
            # Format create_time as string
            create_time_str = process["create_time"].strftime("%Y-%m-%d %H:%M:%S")
            # Truncate command if too long
            command = process["command"][:47] + "..." if len(process["command"]) > 50 else process["command"]
            line = f"{command:<50} {process['pid']:<8} {process['name'][:19]:<20} {process['username'][:11]:<12} {process['cpu_percent']:<8.1f} {process['memory_usage_mb']:<12.2f} {process['status'][:11]:<12} {create_time_str:<20}"
            lines.append(line)
        return "\n".join(lines)

    def choose_and_kill(self):
        # header for interactive process selection
        title = "🎯  INTERACTIVE PROCESS SELECTION AND TERMINATION"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
        # Format data as table for display
        formatted_data = self._format_process_table()
        all_lines = formatted_data.split("\n")
        header_and_separator = all_lines[:2]  # First two lines: header and separator
        options = all_lines[2:]  # Skip header and separator, only process lines
        res = choose_from_options(options=all_lines, msg="📋 Select processes to manage:", tv=True, multi=True)
        # Filter out header and separator if they were selected
        selected_lines = [line for line in res if line not in header_and_separator]
        indices = [options.index(val) for val in selected_lines]
        selected_processes = [self.data[i] for i in indices]
        print("\n📊 All Processes:")
        print(formatted_data)
        print("\n🎯 Selected Processes:")
        for process in selected_processes:
            print(f"PID: {process['pid']}, Name: {process['name']}, Memory: {process['memory_usage_mb']:.2f}MB")
        for idx, process in enumerate(selected_processes):
            pprint(dict(process), f"📌 Process {idx}")
        kill_all = input("\n⚠️  Confirm killing ALL selected processes? y/[n] ").lower() == "y"
        if kill_all:
            self.kill(pids=[p["pid"] for p in selected_processes])
            return
        kill_by_index = input("\n🔫 Kill by index? (enter numbers separated by spaces, e.g. '1 4') or [n] to cancel: ")
        if kill_by_index != "" and kill_by_index != "n":
            indices = [int(val) for val in kill_by_index.split(" ")]
            target_processes = [selected_processes[i] for i in indices]
            for idx2, process in enumerate(target_processes):
                pprint(dict(process), f"🎯 Target Process {idx2}")
            _ = self.kill(pids=[p["pid"] for p in target_processes]) if input("\n⚠️  Confirm termination? y/[n] ").lower() == "y" else None
        console.print(Panel("🔔 No processes were terminated.", title="[bold blue]Process Info[/bold blue]", border_style="blue"))

    def filter_and_kill(self, name: Optional[str] = None):
        # header for filtering processes by name
        title = "🔍  FILTERING AND TERMINATING PROCESSES BY NAME"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
        # Filter processes by name
        filtered_processes = [p for p in self.data if p["name"] == name]
        # Sort by create_time (ascending)
        filtered_processes.sort(key=lambda x: x["create_time"])
        print(f"🎯 Found {len(filtered_processes)} processes matching name: '{name}'")
        self.kill(pids=[p["pid"] for p in filtered_processes])
        console.print(Panel("", title="[bold blue]Process Info[/bold blue]", border_style="blue"))

    def kill(self, names: Optional[list[str]] = None, pids: Optional[list[int]] = None, commands: Optional[list[str]] = None):
        title = "💀  PROCESS TERMINATION"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
        if names is None and pids is None and commands is None:
            print("❌ Error: No termination targets specified (names, pids, or commands)")
            raise ValueError("names, pids and commands cannot all be None")
        if names is None:
            names = []
        if pids is None:
            pids = []
        if commands is None:
            commands = []
        killed_count = 0
        for name in names:
            matching_processes = [p for p in self.data if p["name"] == name]
            if len(matching_processes) > 0:
                for process in matching_processes:
                    psutil.Process(process["pid"]).kill()
                    print(f"💀 Killed process {name} with PID {process['pid']}. It lived {get_age(process['create_time'])}. RIP 💐")
                    killed_count += 1
            else:
                print(f'❓ No process named "{name}" found')
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc_lifetime = get_age(datetime.fromtimestamp(proc.create_time(), tz=None))
                proc.kill()
                print(f'💀 Killed process with PID {pid} and name "{proc_name}". It lived {proc_lifetime}. RIP 💐')
                killed_count += 1
            except psutil.NoSuchProcess:
                print(f"❓ No process with PID {pid} found")
        for command in commands:
            matching_processes = [p for p in self.data if command in p["command"]]
            if len(matching_processes) > 0:
                for process in matching_processes:
                    psutil.Process(process["pid"]).kill()
                    print(f'💀 Killed process with "{command}" in its command & PID {process["pid"]}. It lived {get_age(process["create_time"])}. RIP 💐')
                    killed_count += 1
            else:
                print(f'❓ No process has "{command}" in its command.')
        console.print(Panel(f"✅ Termination complete: {killed_count} processes terminated", title="[bold blue]Process Info[/bold blue]", border_style="blue"))


def get_age(create_time: datetime) -> str:
    dtm_now = datetime.now()
    delta = dtm_now - create_time
    return str(delta).split(".")[0]  # remove microseconds


def main():
    from machineconfig.utils.procs import ProcessManager
    ProcessManager().choose_and_kill()


if __name__ == "__main__":
    pass
