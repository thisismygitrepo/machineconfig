from typing import Any, Optional
from rich.console import Console

console = Console()


def print_global_summary(global_summary: dict[str, Any], title: str) -> None:
    print("=" * 80)
    print(f"🖥️  {title}")
    print("=" * 80)
    print("🌐 GLOBAL SUMMARY:")
    print(f"   Total sessions: {global_summary['total_sessions']}")
    print(f"   Healthy sessions: {global_summary['healthy_sessions']}")
    print(f"   Total commands: {global_summary['total_commands']}")
    print(f"   Running commands: {global_summary['running_commands']}")
    if "remote_machines" in global_summary:
        print(f"   Remote machines: {len(global_summary['remote_machines'])}")
    print(f"   All healthy: {'✅' if global_summary['all_sessions_healthy'] else '❌'}")
    print()


def print_session_health_status(wt_status: dict[str, Any], remote_name: Optional[str] = None) -> None:
    location_str = f" on {remote_name}" if remote_name else ""
    if wt_status.get("wt_running", False):
        if wt_status.get("session_exists", False):
            session_windows = wt_status.get("session_windows", [])
            all_windows = wt_status.get("all_windows", [])
            print(f"✅ Windows Terminal is running{location_str}")
            print(f"   Session windows: {len(session_windows)}")
            print(f"   Total WT windows: {len(all_windows)}")
        else:
            print(f"⚠️  Windows Terminal is running but no session windows found{location_str}")
    else:
        print(f"❌ Windows Terminal issue{location_str}: {wt_status.get('error', 'Unknown error')}")


def print_commands_status(commands_status: dict[str, dict[str, Any]], summary: dict[str, int]) -> None:
    print(f"   Commands ({summary['running_commands']}/{summary['total_commands']} running):")
    for tab_name, cmd_status in commands_status.items():
        status_icon = "✅" if cmd_status.get("running", False) else "❌"
        cmd_text = cmd_status.get("command", "Unknown")[:50]
        if len(cmd_status.get("command", "")) > 50:
            cmd_text += "..."
        console.print(f"     {status_icon} {tab_name}: {cmd_text}")
        if cmd_status.get("processes"):
            for proc in cmd_status["processes"][:2]:
                console.print(f"        [dim]└─[/dim] PID {proc.get('pid', 'Unknown')}: {proc.get('name', 'Unknown')}")


def calculate_session_summary(commands_status: dict[str, dict[str, Any]], session_healthy: bool) -> dict[str, Any]:
    running_count = sum(1 for status in commands_status.values() if status.get("running", False))
    total_count = len(commands_status)
    return {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": session_healthy}


def calculate_global_summary_from_status(all_status: dict[str, dict[str, Any]], include_remote_machines: bool = False) -> dict[str, Any]:
    total_sessions = len(all_status)
    healthy_sessions = sum(1 for status in all_status.values() if status.get("summary", {}).get("session_healthy", False))
    total_commands = sum(status.get("summary", {}).get("total_commands", 0) for status in all_status.values())
    total_running = sum(status.get("summary", {}).get("running_commands", 0) for status in all_status.values())
    
    result: dict[str, Any] = {
        "total_sessions": total_sessions,
        "healthy_sessions": healthy_sessions,
        "unhealthy_sessions": total_sessions - healthy_sessions,
        "total_commands": total_commands,
        "running_commands": total_running,
        "stopped_commands": total_commands - total_running,
        "all_sessions_healthy": healthy_sessions == total_sessions,
        "all_commands_running": total_running == total_commands,
    }
    
    if include_remote_machines:
        result["remote_machines"] = list(set(status.get("remote_name", "") for status in all_status.values() if "remote_name" in status))
    
    return result
