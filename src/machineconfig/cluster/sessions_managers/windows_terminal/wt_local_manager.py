#!/usr/bin/env python3
from datetime import datetime
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Any, TypedDict, cast

from rich import box
from rich.console import Console
from rich.table import Table
from machineconfig.utils.scheduler import Scheduler
from machineconfig.cluster.sessions_managers.windows_terminal.wt_local import WTLayoutGenerator
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.wt_helpers import check_wt_session_status
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import StartResult, ActiveSessionInfo
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.manager_persistence import (
    generate_session_id, save_json_file, load_json_file, list_saved_sessions_in_dir, delete_session_dir, ensure_session_dir_exists
)
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.status_reporting import (
    print_global_summary, print_session_health_status, print_commands_status, calculate_session_summary, calculate_global_summary_from_status
)




TMP_SERIALIZATION_DIR = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
console = Console()


class _MonitoringRow(TypedDict):
    session: str
    tab: str
    running: bool
    runTime: str
    command: str
    processes: int


def _format_runtime_seconds(total_seconds: float) -> str:
    total_seconds_int = max(0, int(total_seconds))
    hours, remainder = divmod(total_seconds_int, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"""{hours:02d}:{minutes:02d}:{seconds:02d}"""


def _update_runtime_tracker(
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


class _LoadedManagerData(TypedDict):
    session_name: str
    layout_config: LayoutConfig
    script_path: str | None



class WTLocalManager:
    """Manages multiple local Windows Terminal sessions and monitors their tabs and processes."""

    def __init__(self, session_layouts: list[LayoutConfig], session_name_prefix: Optional[str]):
        """
        Initialize the local Windows Terminal manager.

        Args:
            session_layouts: Dict mapping session names to their layout configs
                Format: {session_name: LayoutConfig, ...}
            session_name_prefix: Prefix for session names
        """
        self.session_name_prefix: str | None = session_name_prefix
        self.session_layouts = session_layouts  # Store the original config
        self.managers: list[WTLayoutGenerator] = []

        # Create a WTLayoutGenerator for each session
        for layout_config in session_layouts:
            session_name = layout_config["layoutName"]
            manager = WTLayoutGenerator(layout_config=layout_config, session_name=session_name)
            manager.create_layout_file()
            self.managers.append(manager)


        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        # console = Console()
        self.logger = logger
        self.logger.info(f"Initialized WTLocalManager with {len(self.managers)} sessions")
    def get_all_session_names(self) -> list[str]:
        """Get all managed session names."""
        return [manager.session_name for manager in self.managers]

    def start_all_sessions(self) -> dict[str, StartResult]:
        """Start all Windows Terminal sessions with their layouts."""
        results: dict[str, StartResult] = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                script_path = manager.script_path

                if not script_path:
                    results[session_name] = {"success": False, "error": "No script file path available"}
                    continue

                # Execute the PowerShell script to start Windows Terminal
                cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}"'

                self.logger.info(f"Starting session '{session_name}' with script: {script_path}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    results[session_name] = {"success": True, "message": f"Session '{session_name}' started successfully"}
                    self.logger.info(f"✅ Session '{session_name}' started successfully")
                else:
                    results[session_name] = {"success": False, "error": result.stderr or result.stdout}
                    self.logger.error(f"❌ Failed to start session '{session_name}': {result.stderr}")

            except Exception as e:
                results[session_name] = {"success": False, "error": str(e)}
                self.logger.error(f"❌ Exception starting session '{session_name}': {e}")

        return results

    def kill_all_sessions(self) -> dict[str, StartResult]:
        """Kill all managed Windows Terminal sessions."""
        results: dict[str, StartResult] = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                # Kill all Windows Terminal processes (Windows Terminal doesn't have session-specific killing)
                cmd = "powershell -Command \"Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force\""

                self.logger.info(f"Killing Windows Terminal processes for session '{session_name}'")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

                results[session_name] = {"success": result.returncode == 0, "message": "Windows Terminal processes killed" if result.returncode == 0 else result.stderr}

            except Exception as e:
                results[session_name] = {"success": False, "error": str(e)}

        return results

    def attach_to_session(self, session_name: Optional[str] = None) -> str:
        """
        Generate command to attach to a specific session or list attachment commands for all.

        Args:
            session_name: Specific session to attach to, or None for all sessions

        Returns:
            Command string to attach to session(s)
        """
        if session_name:
            # Find the specific session
            for manager in self.managers:
                if manager.session_name == session_name:
                    return f"wt -w {session_name}"
            raise ValueError(f"Session '{session_name}' not found")
        else:
            # Return commands for all sessions
            commands = []
            for manager in self.managers:
                commands.append(f"# Attach to session '{manager.session_name}':")
                commands.append(f"wt -w {manager.session_name}")
                commands.append("")
            return "\n".join(commands)

    def check_all_sessions_status(self) -> dict[str, dict[str, Any]]:
        status_report = {}
        for manager in self.managers:
            session_name = manager.session_name or "default"
            session_status = check_wt_session_status(session_name)
            commands_status = manager.check_all_commands_status()
            summary = calculate_session_summary(commands_status, session_status.get("session_exists", False))
            status_report[session_name] = {"session_status": session_status, "commands_status": commands_status, "summary": summary}
        return status_report

    def get_global_summary(self) -> dict[str, Any]:
        all_status = self.check_all_sessions_status()
        return calculate_global_summary_from_status(all_status, include_remote_machines=False)

    def print_status_report(self) -> None:
        all_status = self.check_all_sessions_status()
        global_summary = self.get_global_summary()
        print_global_summary(global_summary, "WINDOWS TERMINAL LOCAL MANAGER STATUS REPORT")
        for session_name, status in all_status.items():
            print(f"🪟 SESSION: {session_name}")
            print("-" * 60)
            print_session_health_status(status["session_status"], remote_name=None)
            print_commands_status(status["commands_status"], status["summary"])
            print()
        print("=" * 80)

    def run_monitoring_routine(self, wait_ms: int = 30000) -> None:
        """
        Run a continuous monitoring routine that checks status periodically.

        Args:
            wait_ms: How long to wait between checks in milliseconds (default: 30000ms = 30s)
        """

        runtime_seconds_by_key: dict[tuple[str, str], float] = {}
        last_runtime_update = time.monotonic()

        def routine(scheduler: Scheduler) -> None:
            nonlocal last_runtime_update
            print(f"\n⏰ Monitoring cycle {scheduler.cycle} at {datetime.now()}")
            print("-" * 50)

            all_status = self.check_all_sessions_status()
            now = time.monotonic()
            elapsed_seconds = max(0.0, now - last_runtime_update)
            last_runtime_update = now
            _update_runtime_tracker(all_status, runtime_seconds_by_key, elapsed_seconds)

            if scheduler.cycle % 2 == 0:
                status_rows: list[_MonitoringRow] = []
                for session_name, status in all_status.items():
                    for tab_name, cmd_status in status["commands_status"].items():
                        key = (session_name, tab_name)
                        command = cmd_status.get("command", "Unknown")
                        command_display = command if len(command) <= 60 else f"""{command[:57]}..."""
                        status_rows.append(
                            {
                                "session": session_name,
                                "tab": tab_name,
                                "running": cmd_status.get("running", False),
                                "runTime": _format_runtime_seconds(runtime_seconds_by_key.get(key, 0.0)),
                                "command": command_display,
                                "processes": len(cmd_status.get("processes", [])),
                            }
                        )

                if status_rows:
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

                    running_count = sum(1 for row in status_rows if row.get("running", False))
                    if running_count == 0:
                        print("\n⚠️  All commands have stopped. Stopping monitoring.")
                        scheduler.max_cycles = scheduler.cycle
                        return
                else:
                    print("No status data available")
            else:
                global_summary = calculate_global_summary_from_status(all_status, include_remote_machines=False)
                print(f"""📊 Quick Summary: {global_summary['running_commands']}/{global_summary['total_commands']} commands running across {global_summary['healthy_sessions']}/{global_summary['total_sessions']} sessions""")

        self.logger.info(f"Starting monitoring routine with {wait_ms}ms intervals")
        from machineconfig.utils.scheduler import LoggerTemplate
        from typing import cast
        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=cast(LoggerTemplate, self.logger))
        sched.run(max_cycles=None)

    def save(self, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = generate_session_id()
        session_dir = TMP_SERIALIZATION_DIR / session_id
        ensure_session_dir_exists(session_dir)
        save_json_file(session_dir / "session_layouts.json", self.session_layouts, "session layouts")
        metadata = {"session_name_prefix": self.session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(self.managers), "sessions": [item["layoutName"] for item in self.session_layouts], "manager_type": "WTLocalManager"}
        save_json_file(session_dir / "metadata.json", metadata, "metadata")
        managers_dir = session_dir / "managers"
        managers_dir.mkdir(exist_ok=True)
        for i, manager in enumerate(self.managers):
            manager_data = {"session_name": manager.session_name, "layout_config": manager.layout_config, "script_path": manager.script_path}
            save_json_file(managers_dir / f"manager_{i}_{manager.session_name}.json", manager_data, f"manager {i}")
        self.logger.info(f"✅ Saved WTLocalManager session to: {session_dir}")
        return session_id

    @staticmethod
    def load(session_id: str) -> "WTLocalManager":
        session_dir = TMP_SERIALIZATION_DIR / session_id
        if not session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        loaded_data = load_json_file(session_dir / "session_layouts.json", "Configuration file")
        session_layouts = loaded_data if isinstance(loaded_data, list) else []
        metadata_data = load_json_file(session_dir / "metadata.json", "Metadata file") if (session_dir / "metadata.json").exists() else {}
        metadata = metadata_data if isinstance(metadata_data, dict) else {}
        session_name_prefix = metadata.get("session_name_prefix", None)
        instance = WTLocalManager(session_layouts=session_layouts, session_name_prefix=session_name_prefix)
        managers_dir = session_dir / "managers"
        if managers_dir.exists():
            instance.managers = []
            for manager_file in sorted(managers_dir.glob("manager_*.json")):
                try:
                    loaded_manager_data = load_json_file(manager_file, "Manager data")
                    manager_data = cast(_LoadedManagerData, loaded_manager_data) if isinstance(loaded_manager_data, dict) else None
                    if manager_data is None:
                        raise ValueError("Invalid manager data format")
                    manager = WTLayoutGenerator(layout_config=manager_data["layout_config"], session_name=manager_data["session_name"])
                    manager.script_path = manager_data["script_path"]
                    instance.managers.append(manager)
                except Exception as e:
                    instance.logger.warning(f"Failed to load manager from {manager_file}: {e}")
        instance.logger.info(f"✅ Loaded WTLocalManager session from: {session_dir}")
        return instance

    @staticmethod
    def list_saved_sessions() -> list[str]:
        return list_saved_sessions_in_dir(TMP_SERIALIZATION_DIR)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        return delete_session_dir(TMP_SERIALIZATION_DIR / session_id, session_id)

    def list_active_sessions(self) -> list[ActiveSessionInfo]:
        active_sessions: list[ActiveSessionInfo] = []

        try:
            result = subprocess.run(
                ["powershell", "-Command", 'Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle | ConvertTo-Json -Depth 2'], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                import json

                all_processes = json.loads(result.stdout.strip())
                if not isinstance(all_processes, list):
                    all_processes = [all_processes]

                for manager in self.managers:
                    session_name = manager.session_name
                    session_windows = []

                    for proc in all_processes:
                        window_title = proc.get("MainWindowTitle", "")
                        if session_name in window_title or not window_title:
                            session_windows.append(proc)

                    active_sessions.append(
                        {
                            "session_name": session_name,
                            "is_active": len(session_windows) > 0,
                            "tab_count": len(manager.layout_config["layoutTabs"]) if manager.layout_config else 0,
                            "tabs": [tab["tabName"] for tab in manager.layout_config["layoutTabs"]] if manager.layout_config else [],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error listing active sessions: {e}")

        return active_sessions

    def get_wt_overview(self) -> dict[str, Any]:
        """Get overview of all Windows Terminal windows and processes."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 'Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle, CPU | ConvertTo-Json -Depth 2'], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                import json

                processes = json.loads(result.stdout.strip())
                if not isinstance(processes, list):
                    processes = [processes]

                return {"success": True, "total_windows": len(processes), "windows": processes, "managed_sessions": len(self.managers)}
            else:
                return {"success": True, "total_windows": 0, "windows": [], "managed_sessions": len(self.managers), "message": "No Windows Terminal processes found"}
        except Exception as e:
            return {"success": False, "error": str(e), "managed_sessions": len(self.managers)}


if __name__ == "__main__":
    # Example usage with new schema
    sample_sessions: list[LayoutConfig] = [
        {
            "layoutName": "DevelopmentEnv",
            "layoutTabs": [
                {"tabName": "🚀Frontend", "startDir": "~/code/myapp/frontend", "command": "bun run dev"},
                {"tabName": "⚙️Backend", "startDir": "~/code/myapp/backend", "command": "python manage.py runserver"},
                {"tabName": "📊Monitor", "startDir": "~", "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"},
            ],
        },
        {
            "layoutName": "TestingEnv",
            "layoutTabs": [
                {"tabName": "🧪Tests", "startDir": "~/code/myapp", "command": "pytest --watch"},
                {"tabName": "🔍Coverage", "startDir": "~/code/myapp", "command": "python -m coverage run --source=. -m pytest"},
                {"tabName": "📝Logs", "startDir": "~/logs", "command": "Get-Content app.log -Wait"},
            ],
        },
        {
            "layoutName": "DeploymentEnv",
            "layoutTabs": [
                {"tabName": "🐳Docker", "startDir": "~/code/myapp", "command": "docker-compose up"},
                {"tabName": "☸️K8s", "startDir": "~/k8s", "command": "kubectl get pods --watch"},
                {"tabName": "📈Metrics", "startDir": "~", "command": 'Get-Counter "\\Processor(_Total)\\% Processor Time" -SampleInterval 2 -MaxSamples 30'},
            ],
        },
    ]

    try:
        # Create the local manager
        manager = WTLocalManager(sample_sessions, session_name_prefix="DevEnv")
        print(f"✅ Local manager created with {len(manager.managers)} sessions")

        # Show session names
        print(f"📋 Sessions: {manager.get_all_session_names()}")

        # Print attachment commands (without actually starting)
        print("\n📎 Attachment commands:")
        print(manager.attach_to_session())

        # Show current status
        print("\n🔍 Current status:")
        manager.print_status_report()

        # Show Windows Terminal overview
        print("\n🖥️  Windows Terminal Overview:")
        overview = manager.get_wt_overview()
        if overview["success"]:
            print(f"   Total WT windows: {overview['total_windows']}")
            print(f"   Managed sessions: {overview['managed_sessions']}")
        else:
            print(f"   Error: {overview.get('error', 'Unknown')}")

        # Demonstrate save/load
        print("\n💾 Demonstrating save/load...")
        session_id = manager.save()
        print(f"✅ Saved session: {session_id}")

        # List saved sessions
        saved_sessions = WTLocalManager.list_saved_sessions()
        print(f"📋 Saved sessions: {saved_sessions}")

        # Load and verify
        loaded_manager = WTLocalManager.load(session_id)
        print(f"✅ Loaded session with {len(loaded_manager.managers)} sessions")

        # Show how to start monitoring (commented out to prevent infinite loop in demo)
        print("\n⏰ To start monitoring, run:")
        print("manager.run_monitoring_routine(wait_ms=30000)  # 30 seconds")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
