from typing import Any, TypedDict

from rich import box
from rich.console import Console
from rich.table import Table


class MonitoringRow(TypedDict):
    session: str
    tab: str
    running: bool
    runTime: str
    command: str
    processes: int


def format_runtime_seconds(total_seconds: float) -> str:
    total_seconds_int = max(0, int(total_seconds))
    hours, remainder = divmod(total_seconds_int, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"""{hours:02d}:{minutes:02d}:{seconds:02d}"""


def update_runtime_tracker(
    all_status: dict[str, dict[str, Any]],
    runtime_seconds_by_key: dict[tuple[str, str], float],
    elapsed_seconds: float,
) -> None:
    for session_name, status in all_status.items():
        for tab_name, cmd_status in status["commands_status"].items():
            key = (session_name, tab_name)
            runtime_seconds = runtime_seconds_by_key.get(key, 0.0)
            if cmd_status.get("running", False):
                runtime_seconds_by_key[key] = runtime_seconds + elapsed_seconds
            else:
                runtime_seconds_by_key.setdefault(key, runtime_seconds)


def build_monitoring_rows(
    all_status: dict[str, dict[str, Any]],
    runtime_seconds_by_key: dict[tuple[str, str], float],
    max_command_length: int,
) -> list[MonitoringRow]:
    status_rows: list[MonitoringRow] = []
    for session_name, status in all_status.items():
        for tab_name, cmd_status in status["commands_status"].items():
            key = (session_name, tab_name)
            command = cmd_status.get("command", "Unknown")
            command_display = command if len(command) <= max_command_length else f"""{command[:max_command_length - 3]}..."""
            status_rows.append(
                {
                    "session": session_name,
                    "tab": tab_name,
                    "running": cmd_status.get("running", False),
                    "runTime": format_runtime_seconds(runtime_seconds_by_key.get(key, 0.0)),
                    "command": command_display,
                    "processes": len(cmd_status.get("processes", [])),
                }
            )
    return status_rows


def print_monitoring_table(status_rows: list[MonitoringRow], console: Console) -> int:
    table = Table(title="📊 Windows Terminal Monitoring", show_header=True, header_style="bold cyan", box=box.ROUNDED)
    table.add_column("Session", style="cyan", no_wrap=True)
    table.add_column("Tab", style="magenta", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("runTime", justify="right", style="yellow")
    table.add_column("Processes", justify="right", style="blue")
    table.add_column("Command", style="green", max_width=60)

    for row in status_rows:
        status_text = "[bold green]✅ Running[/bold green]" if row["running"] else "[bold red]❌ Stopped[/bold red]"
        table.add_row(row["session"], row["tab"], status_text, row["runTime"], str(row["processes"]), row["command"])

    console.print(table)
    return sum(1 for row in status_rows if row.get("running", False))


def print_quick_summary(global_summary: dict[str, Any]) -> None:
    print(
        f"""📊 Quick Summary: {global_summary['running_commands']}/{global_summary['total_commands']} commands running across {global_summary['healthy_sessions']}/{global_summary['total_sessions']} sessions"""
    )
