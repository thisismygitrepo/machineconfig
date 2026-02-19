#!/usr/bin/env python3
from datetime import datetime
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Any, TypedDict, cast

from rich.console import Console
from machineconfig.utils.scheduler import Scheduler, LoggerTemplate
from machineconfig.cluster.sessions_managers.windows_terminal.wt_local import WTLayoutGenerator
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.wt_helpers import check_wt_session_status
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import StartResult, ActiveSessionInfo
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.manager_persistence import (
    generate_session_id, save_json_file, load_json_file, list_saved_sessions_in_dir, delete_session_dir, ensure_session_dir_exists
)
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.local_monitoring import (
    update_runtime_tracker, build_monitoring_rows, print_monitoring_table, print_quick_summary
)
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.status_reporting import (
    print_global_summary, print_session_health_status, print_commands_status, calculate_session_summary, calculate_global_summary_from_status
)




TMP_SERIALIZATION_DIR = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
console = Console()


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
            wt_manager = WTLayoutGenerator(layout_config=layout_config, session_name=session_name)
            wt_manager.create_layout_file()
            self.managers.append(wt_manager)


        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        # console = Console()
        self.logger = logger
        self.logger.info(f"Initialized WTLocalManager with {len(self.managers)} sessions")
    def get_all_session_names(self) -> list[str]:
        """Get all managed session names."""
        return [wt_manager.session_name for wt_manager in self.managers]

    def start_all_sessions(self) -> dict[str, StartResult]:
        """Start all Windows Terminal sessions with their layouts."""
        results: dict[str, StartResult] = {}
        for wt_manager in self.managers:
            session_name = wt_manager.session_name or "unknown"
            try:
                script_path = wt_manager.script_path

                if not script_path:
                    results[session_name] = {"success": False, "error": "No script file path available"}
                    continue

                # Execute the PowerShell script to start Windows Terminal
                cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}"'

                self.logger.info(f"Starting session '{session_name}' with script: {script_path}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, check=False)

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
        for wt_manager in self.managers:
            session_name = wt_manager.session_name or "unknown"
            try:
                # Kill all Windows Terminal processes (Windows Terminal doesn't have session-specific killing)
                cmd = "powershell -Command \"Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force\""

                self.logger.info(f"Killing Windows Terminal processes for session '{session_name}'")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, check=False)

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
            for wt_manager in self.managers:
                if wt_manager.session_name == session_name:
                    return f"wt -w {session_name}"
            raise ValueError(f"Session '{session_name}' not found")
        else:
            # Return commands for all sessions
            commands = []
            for wt_manager in self.managers:
                commands.append(f"# Attach to session '{wt_manager.session_name}':")
                commands.append(f"wt -w {wt_manager.session_name}")
                commands.append("")
            return "\n".join(commands)

    def check_all_sessions_status(self) -> dict[str, dict[str, Any]]:
        status_report = {}
        for wt_manager in self.managers:
            session_name = wt_manager.session_name or "default"
            session_status = check_wt_session_status(session_name)
            commands_status = wt_manager.check_all_commands_status()
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
            update_runtime_tracker(all_status, runtime_seconds_by_key, elapsed_seconds)

            if scheduler.cycle % 2 == 0:
                status_rows = build_monitoring_rows(all_status, runtime_seconds_by_key, max_command_length=60)

                if status_rows:
                    running_count = print_monitoring_table(status_rows, console)
                    if running_count == 0:
                        print("\n⚠️  All commands have stopped. Stopping monitoring.")
                        scheduler.max_cycles = scheduler.cycle
                        return
                else:
                    print("No status data available")
            else:
                global_summary = calculate_global_summary_from_status(all_status, include_remote_machines=False)
                print_quick_summary(global_summary)

        self.logger.info(f"Starting monitoring routine with {wait_ms}ms intervals")
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
        for i, wt_manager in enumerate(self.managers):
            manager_data = {"session_name": wt_manager.session_name, "layout_config": wt_manager.layout_config, "script_path": wt_manager.script_path}
            save_json_file(managers_dir / f"manager_{i}_{wt_manager.session_name}.json", manager_data, f"manager {i}")
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
                    wt_manager = WTLayoutGenerator(layout_config=manager_data["layout_config"], session_name=manager_data["session_name"])
                    wt_manager.script_path = manager_data["script_path"]
                    instance.managers.append(wt_manager)
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
                ["powershell", "-Command", 'Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle | ConvertTo-Json -Depth 2'], capture_output=True, text=True, timeout=10, check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                import json

                all_processes = json.loads(result.stdout.strip())
                if not isinstance(all_processes, list):
                    all_processes = [all_processes]

                for wt_manager in self.managers:
                    session_name = wt_manager.session_name
                    session_windows = []

                    for proc in all_processes:
                        window_title = proc.get("MainWindowTitle", "")
                        if session_name in window_title or not window_title:
                            session_windows.append(proc)

                    active_sessions.append(
                        {
                            "session_name": session_name,
                            "is_active": len(session_windows) > 0,
                            "tab_count": len(wt_manager.layout_config["layoutTabs"]) if wt_manager.layout_config else 0,
                            "tabs": [tab["tabName"] for tab in wt_manager.layout_config["layoutTabs"]] if wt_manager.layout_config else [],
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error listing active sessions: {e}")

        return active_sessions

    def get_wt_overview(self) -> dict[str, Any]:
        """Get overview of all Windows Terminal windows and processes."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", 'Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle, CPU | ConvertTo-Json -Depth 2'], capture_output=True, text=True, timeout=10, check=False
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
    from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.examples.wt_local_manager_demo import run_demo

    run_demo()
