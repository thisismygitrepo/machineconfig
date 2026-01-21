#!/usr/bin/env python3
from datetime import datetime
import subprocess
from typing import Any, Optional, TypedDict, cast

from machineconfig.logger import get_logger
from machineconfig.utils.scheduler import Scheduler
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.tmux.tmux_local import TmuxLayoutGenerator, TmuxLayoutSummary
from machineconfig.cluster.sessions_managers.tmux.tmux_utils.tmux_helpers import check_tmux_session_status, build_unknown_command_status, TmuxSessionStatus
from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import StartResult, CommandStatus
from machineconfig.cluster.sessions_managers.windows_terminal.wt_utils.status_reporting import calculate_global_summary_from_status


logger = get_logger("cluster.sessions_managers.tmux_local_manager")


class TmuxSessionReport(TypedDict):
    session_status: TmuxSessionStatus
    commands_status: dict[str, CommandStatus]
    summary: TmuxLayoutSummary


class TmuxLocalManager:
    def __init__(self, session_layouts: list[LayoutConfig], session_name_prefix: Optional[str]) -> None:
        self.session_name_prefix: Optional[str] = session_name_prefix
        self.session_layouts = session_layouts
        self.managers: list[TmuxLayoutGenerator] = []
        for layout_config in session_layouts:
            session_name = layout_config["layoutName"].replace(" ", "_")
            if self.session_name_prefix is not None:
                full_session_name = f"{self.session_name_prefix}_{session_name}"
            else:
                full_session_name = session_name
            manager = TmuxLayoutGenerator(layout_config=layout_config, session_name=full_session_name)
            manager.create_layout_file()
            self.managers.append(manager)
        logger.info(f"Initialized TmuxLocalManager with {len(self.managers)} sessions")

    def get_all_session_names(self) -> list[str]:
        return [manager.session_name for manager in self.managers]

    def start_all_sessions(self) -> dict[str, StartResult]:
        results: dict[str, StartResult] = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                script_path = manager.script_path
                if script_path is None:
                    results[session_name] = {"success": False, "error": "No script file path available"}
                    continue
                result = subprocess.run(["bash", script_path], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    results[session_name] = {"success": True, "message": f"Session '{session_name}' started successfully"}
                else:
                    results[session_name] = {"success": False, "error": result.stderr or result.stdout}
            except Exception as exc:
                results[session_name] = {"success": False, "error": str(exc)}
        return results

    def kill_all_sessions(self) -> dict[str, StartResult]:
        results: dict[str, StartResult] = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                result = subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    results[session_name] = {"success": True, "message": "Session killed"}
                else:
                    results[session_name] = {"success": False, "error": result.stderr or result.stdout}
            except Exception as exc:
                results[session_name] = {"success": False, "error": str(exc)}
        return results

    def attach_to_session(self, session_name: Optional[str]) -> str:
        if session_name is None:
            commands = []
            for manager in self.managers:
                commands.append(f"# Attach to session '{manager.session_name}':")
                commands.append(f"tmux attach -t {manager.session_name}")
                commands.append("")
            return "\n".join(commands)
        for manager in self.managers:
            if manager.session_name == session_name:
                return f"tmux attach -t {session_name}"
        raise ValueError(f"Session '{session_name}' not found")

    def check_all_sessions_status(self) -> dict[str, TmuxSessionReport]:
        status_report: dict[str, TmuxSessionReport] = {}
        for manager in self.managers:
            session_name = manager.session_name or "default"
            session_status = check_tmux_session_status(session_name)
            commands_status: dict[str, CommandStatus] = {}
            if manager.layout_config:
                for tab in manager.layout_config["layoutTabs"]:
                    commands_status[tab["tabName"]] = build_unknown_command_status(tab)
            summary: TmuxLayoutSummary = {
                "total_commands": len(commands_status),
                "running_commands": sum(1 for status in commands_status.values() if status.get("running", False)),
                "stopped_commands": sum(1 for status in commands_status.values() if not status.get("running", False)),
                "session_healthy": session_status.get("session_exists", False),
            }
            status_report[session_name] = {"session_status": session_status, "commands_status": commands_status, "summary": summary}
        return status_report

    def get_global_summary(self) -> dict[str, object]:
        all_status = self.check_all_sessions_status()
        return calculate_global_summary_from_status(cast(dict[str, dict[str, Any]], all_status), include_remote_machines=False)

    def print_status_report(self) -> None:
        all_status = self.check_all_sessions_status()
        global_summary = self.get_global_summary()
        print("=" * 80)
        print("🧩 TMUX LOCAL MANAGER STATUS REPORT")
        print("=" * 80)
        print(f"Total sessions: {global_summary['total_sessions']}")
        print(f"Healthy sessions: {global_summary['healthy_sessions']}")
        print(f"Total commands: {global_summary['total_commands']}")
        print(f"Running commands: {global_summary['running_commands']}")
        print(f"All healthy: {'✅' if global_summary['all_sessions_healthy'] else '❌'}")
        print()
        for session_name, status in all_status.items():
            print(f"TMUX SESSION: {session_name}")
            print("-" * 60)
            session_status = status["session_status"]
            if session_status.get("tmux_running", False):
                if session_status.get("session_exists", False):
                    print("✅ tmux session is running")
                else:
                    print("⚠️  tmux running but session not found")
            else:
                print(f"❌ tmux issue: {session_status.get('error', 'Unknown error')}")
            summary = status["summary"]
            print(f"Commands: {summary['running_commands']}/{summary['total_commands']} running")
            print()
        print("=" * 80)

    def run_monitoring_routine(self, wait_ms: int) -> None:
        def routine(scheduler: Scheduler) -> None:
            print(f"\n⏰ Monitoring cycle {scheduler.cycle} at {datetime.now()}")
            all_status = self.check_all_sessions_status()
            active_sessions = [name for name, status in all_status.items() if status.get("session_status", {}).get("session_exists", False)]
            print(f"Active tmux sessions: {len(active_sessions)}")
            if not active_sessions:
                print("⚠️  No active sessions detected. Stopping monitoring.")
                scheduler.max_cycles = scheduler.cycle
        from machineconfig.utils.scheduler import LoggerTemplate
        from typing import cast
        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=cast(LoggerTemplate, logger))
        sched.run(max_cycles=None)
