#!/usr/bin/env python3
"""
Status reporting utilities for Windows Terminal layouts and sessions.
"""

import logging
from typing import Dict, Any, List
from rich.console import Console
from machineconfig.cluster.sessions_managers.wt_utils.process_monitor import WTProcessMonitor
from machineconfig.cluster.sessions_managers.wt_utils.session_manager import WTSessionManager
from machineconfig.utils.schemas.layouts.layout_types import TabConfig

logger = logging.getLogger(__name__)
console = Console()


class WTStatusReporter:
    """Handles comprehensive status reporting for Windows Terminal sessions."""

    def __init__(self, process_monitor: WTProcessMonitor, session_manager: WTSessionManager):
        self.process_monitor = process_monitor
        self.session_manager = session_manager

    def get_comprehensive_status(self, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Get comprehensive status including Windows Terminal session and all commands."""
        wt_status = self.session_manager.check_wt_session_status()
        commands_status = self.process_monitor.check_all_commands_status(tabs)

        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)

        return {
            "wt_session": wt_status,
            "commands": commands_status,
            "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": wt_status.get("session_exists", False), "location": wt_status.get("location", "unknown")},
        }

    def print_status_report(self, tabs: List[TabConfig]) -> None:
        """Print a comprehensive status report for the Windows Terminal session."""
        status = self.get_comprehensive_status(tabs)
        wt_session = status["wt_session"]
        commands = status["commands"]
        summary = status["summary"]

        print("=" * 80)
        print("🖥️  WINDOWS TERMINAL STATUS REPORT")
        print("=" * 80)

        # Session status
        location = wt_session.get("location", "unknown")
        print(f"📍 Location: {location}")
        print(f"🪟 Session: {self.session_manager.session_name}")

        if wt_session.get("wt_running", False):
            if wt_session.get("session_exists", False):
                session_windows = wt_session.get("session_windows", [])
                all_windows = wt_session.get("all_windows", [])
                print("✅ Windows Terminal is running")
                print(f"   Session windows: {len(session_windows)}")
                print(f"   Total WT windows: {len(all_windows)}")
            else:
                print("⚠️  Windows Terminal is running but no session windows found")
        else:
            error_msg = wt_session.get("error", "Unknown error")
            print(f"❌ Windows Terminal session issue: {error_msg}")

        print()

        # Commands status
        print(f"📋 COMMANDS STATUS ({summary['running_commands']}/{summary['total_commands']} running):")
        print("-" * 60)

        for tab_name, cmd_status in commands.items():
            status_icon = "✅" if cmd_status.get("running", False) else "❌"
            cmd_text = cmd_status.get("command", "Unknown")[:50]
            if len(cmd_status.get("command", "")) > 50:
                cmd_text += "..."

            print(f"  {status_icon} {tab_name}")
            print(f"     Command: {cmd_text}")

            if cmd_status.get("processes"):
                processes = cmd_status["processes"][:3]  # Show first 3 processes
                for proc in processes:
                    pid = proc.get("pid", "Unknown")
                    name = proc.get("name", "Unknown")
                    console.print(f"       [dim]└─[/dim] PID {pid}: {name}")

                if len(cmd_status["processes"]) > 3:
                    remaining = len(cmd_status["processes"]) - 3
                    console.print(f"       [dim]└─[/dim] ... and {remaining} more processes")

            if cmd_status.get("error"):
                print(f"     Error: {cmd_status['error']}")

            print()

        # Summary
        print("📊 SUMMARY:")
        print(f"   Total commands: {summary['total_commands']}")
        print(f"   Running: {summary['running_commands']}")
        print(f"   Stopped: {summary['stopped_commands']}")
        print(f"   Session healthy: {'✅' if summary['session_healthy'] else '❌'}")

        print("=" * 80)

    def get_windows_terminal_overview(self) -> Dict[str, Any]:
        """Get an overview of all Windows Terminal windows and processes."""
        try:
            wt_windows = self.process_monitor.get_windows_terminal_windows()
            wt_version = self.session_manager.get_wt_version()

            return {"success": True, "windows_info": wt_windows, "version_info": wt_version, "location": self.process_monitor.location_name}
        except Exception as e:
            logger.error(f"Failed to get Windows Terminal overview: {e}")
            return {"success": False, "error": str(e), "location": self.process_monitor.location_name}

    def print_windows_terminal_overview(self) -> None:
        """Print an overview of Windows Terminal status."""
        overview = self.get_windows_terminal_overview()

        print("=" * 80)
        print("🖥️  WINDOWS TERMINAL OVERVIEW")
        print("=" * 80)

        if overview["success"]:
            location = overview.get("location", "unknown")
            print(f"📍 Location: {location}")

            # Version info
            version_info = overview.get("version_info", {})
            if version_info.get("success"):
                print(f"📦 Version: {version_info.get('version', 'Unknown')}")
            else:
                print(f"📦 Version: Error getting version - {version_info.get('error', 'Unknown')}")

            # Windows info
            windows_info = overview.get("windows_info", {})
            if windows_info.get("success"):
                windows = windows_info.get("windows", [])
                print(f"🪟 Active Windows: {len(windows)}")

                if windows:
                    print("\nActive Windows:")
                    for i, window in enumerate(windows[:5], 1):  # Show first 5 windows
                        pid = window.get("Id", "Unknown")
                        title = window.get("WindowTitle", "No Title")
                        start_time = window.get("StartTime", "Unknown")
                        print(f"  {i}. PID {pid}: {title} (Started: {start_time})")

                    if len(windows) > 5:
                        print(f"  ... and {len(windows) - 5} more windows")
                else:
                    print("  No Windows Terminal windows currently running")
            else:
                print(f"🪟 Windows Info: Error - {windows_info.get('error', 'Unknown')}")
        else:
            print(f"❌ Failed to get overview: {overview.get('error', 'Unknown')}")

        print("=" * 80)

    def generate_status_summary(self, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Generate a concise status summary suitable for monitoring."""
        try:
            comprehensive_status = self.get_comprehensive_status(tabs)
            wt_overview = self.get_windows_terminal_overview()

            summary = comprehensive_status["summary"]
            wt_status = comprehensive_status["wt_session"]

            return {
                "timestamp": None,  # Will be filled by caller if needed
                "session_name": self.session_manager.session_name,
                "location": summary.get("location", "unknown"),
                "wt_running": wt_status.get("wt_running", False),
                "session_healthy": summary["session_healthy"],
                "total_commands": summary["total_commands"],
                "running_commands": summary["running_commands"],
                "stopped_commands": summary["stopped_commands"],
                "all_commands_running": summary["running_commands"] == summary["total_commands"],
                "wt_windows_count": len(wt_overview.get("windows_info", {}).get("windows", [])) if wt_overview["success"] else 0,
                "wt_version": wt_overview.get("version_info", {}).get("version", "Unknown") if wt_overview["success"] else "Unknown",
            }
        except Exception as e:
            logger.error(f"Failed to generate status summary: {e}")
            return {"error": str(e), "session_name": self.session_manager.session_name, "location": self.process_monitor.location_name}

    def check_tab_specific_status(self, tab_name: str, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Get detailed status for a specific tab."""
        if next((t for t in tabs if t["tabName"] == tab_name), None) is None:
            return {"error": f"Tab '{tab_name}' not found in configuration", "tab_name": tab_name}

        try:
            cmd_status = self.process_monitor.check_command_status(tab_name, tabs)

            # Add additional context
            the_tab = next((t for t in tabs if t["tabName"] == tab_name), None)
            if the_tab is not None:
                cmd_status["tab_config"] = {"working_directory": the_tab["startDir"], "command": the_tab["command"]}

            return cmd_status
        except Exception as e:
            logger.error(f"Failed to check status for tab '{tab_name}': {e}")
            return {"error": str(e), "tab_name": tab_name, "location": self.process_monitor.location_name}
