"""Procs"""

import psutil
from rich.progress import Progress, SpinnerColumn, TextColumn
from zoneinfo import ZoneInfo
from machineconfig.utils.options import display_options
from typing import Optional, Any
from rich.console import Console
from rich.panel import Panel
from datetime import datetime, timezone
from machineconfig.utils.utils2 import pprint

console = Console()

BOX_WIDTH = 78  # width for box drawing


def get_processes_accessing_file(path: str):
    # header for searching processes
    title = "🔍  SEARCHING FOR PROCESSES ACCESSING FILE"
    console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
    res: dict[int, list[str]] = {}

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
    result_data = [{"pid": pid, "files": files} for pid, files in res.items()]
    console.print(Panel(f"✅ Found {len(res)} processes accessing the specified file", title="[bold blue]Process Info[/bold blue]", border_style="blue"))
    return result_data


def kill_process(name: str):
    print(f"⚠️  Attempting to kill process: {name}...")
    killed = False
    for proc in psutil.process_iter():
        if proc.name() == name:
            proc.kill()
            print(f"💀 Process {name} (PID: {proc.pid}) terminated successfully")
            killed = True
    if not killed:
        print(f"❓ No process with name '{name}' was found")
    print(f"{'─' * 80}\n")


class ProcessManager:
    def __init__(self):
        # header for initializing process manager
        title = "📊  INITIALIZING PROCESS MANAGER"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))
        process_info = []

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task("🔍 Reading system processes...", total=None)

            for proc in psutil.process_iter():
                try:
                    mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
                    # Convert create_time to local timezone
                    create_time_utc = datetime.fromtimestamp(proc.create_time(), tz=timezone.utc)
                    create_time_local = create_time_utc.astimezone(ZoneInfo("Australia/Adelaide"))

                    process_info.append(
                        {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "username": proc.username(),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_usage_mb": mem_usage_mb,
                            "status": proc.status(),
                            "create_time": create_time_local,
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
        _headers = ["PID", "Name", "Username", "CPU%", "Memory(MB)", "Status", "Create Time", "Command"]
        header_line = f"{'PID':<8} {'Name':<20} {'Username':<12} {'CPU%':<8} {'Memory(MB)':<12} {'Status':<12} {'Create Time':<20} {'Command':<50}"
        separator = "-" * len(header_line)

        lines = [header_line, separator]

        for process in self.data:
            # Format create_time as string
            create_time_str = process["create_time"].strftime("%Y-%m-%d %H:%M:%S")
            # Truncate command if too long
            command = process["command"][:47] + "..." if len(process["command"]) > 50 else process["command"]

            line = f"{process['pid']:<8} {process['name'][:19]:<20} {process['username'][:11]:<12} {process['cpu_percent']:<8.1f} {process['memory_usage_mb']:<12.2f} {process['status'][:11]:<12} {create_time_str:<20} {command:<50}"
            lines.append(line)

        return "\n".join(lines)

    def choose_and_kill(self):
        # header for interactive process selection
        title = "🎯  INTERACTIVE PROCESS SELECTION AND TERMINATION"
        console.print(Panel(title, title="[bold blue]Process Info[/bold blue]", border_style="blue"))

        # Format data as table for display
        formatted_data = self._format_process_table()
        options = formatted_data.split("\n")[1:]  # Skip header
        res = display_options(options=formatted_data.split("\n"), msg="📋 Select processes to manage:", fzf=True, multi=True)
        indices = [options.index(val) for val in res]
        selected_processes = [self.data[i] for i in indices]

        print("\n📊 All Processes:")
        print(formatted_data)
        print("\n🎯 Selected Processes:")
        for process in selected_processes:
            print(f"PID: {process['pid']}, Name: {process['name']}, Memory: {process['memory_usage_mb']:.2f}MB")

        for idx, process in enumerate(selected_processes):
            pprint(process, f"📌 Process {idx}")

        kill_all = input("\n⚠️  Confirm killing ALL selected processes? y/[n] ").lower() == "y"
        if kill_all:
            self.kill(pids=[p["pid"] for p in selected_processes])
            return

        kill_by_index = input("\n🔫 Kill by index? (enter numbers separated by spaces, e.g. '1 4') or [n] to cancel: ")
        if kill_by_index != "" and kill_by_index != "n":
            indices = [int(val) for val in kill_by_index.split(" ")]
            target_processes = [selected_processes[i] for i in indices]
            for idx2, process in enumerate(target_processes):
                pprint(process, f"🎯 Target Process {idx2}")
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
        # header for process termination
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
                    print(f"💀 Killed process {name} with PID {process['pid']}. It lived {get_age(process['create_time'])}. RIP 🪦💐")
                    killed_count += 1
            else:
                print(f'❓ No process named "{name}" found')

        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc_lifetime = get_age(proc.create_time())
                proc.kill()
                print(f'💀 Killed process with PID {pid} and name "{proc_name}". It lived {proc_lifetime}. RIP 🪦💐')
                killed_count += 1
            except psutil.NoSuchProcess:
                print(f"❓ No process with PID {pid} found")

        for command in commands:
            matching_processes = [p for p in self.data if command in p["command"]]
            if len(matching_processes) > 0:
                for process in matching_processes:
                    psutil.Process(process["pid"]).kill()
                    print(f'💀 Killed process with "{command}" in its command & PID {process["pid"]}. It lived {get_age(process["create_time"])}. RIP 🪦💐')
                    killed_count += 1
            else:
                print(f'❓ No process has "{command}" in its command.')

        console.print(Panel(f"✅ Termination complete: {killed_count} processes terminated", title="[bold blue]Process Info[/bold blue]", border_style="blue"))


def get_age(create_time: Any) -> str:
    """Calculate age from create_time which can be either float timestamp or datetime object."""
    try:
        if isinstance(create_time, (int, float)):
            # Handle timestampz
            create_time_utc = datetime.fromtimestamp(create_time, tz=timezone.utc)
            create_time_local = create_time_utc.astimezone(ZoneInfo("Australia/Adelaide"))
        else:
            # Already a datetime object
            create_time_local = create_time

        now_local = datetime.now(tz=ZoneInfo("Australia/Adelaide"))
        age = now_local - create_time_local
        return str(age)
    except Exception as e:
        try:
            # Fallback without timezone
            if isinstance(create_time, (int, float)):
                create_time_dt = datetime.fromtimestamp(create_time)
            else:
                create_time_dt = create_time.replace(tzinfo=None) if create_time.tzinfo else create_time
            now_dt = datetime.now()
            age = now_dt - create_time_dt
            return str(age)
        except Exception as ee:
            return f"unknown due to {ee} and {e}"


def main():
    from machineconfig.utils.procs import ProcessManager

    ProcessManager().choose_and_kill()


if __name__ == "__main__":
    pass
