#!/usr/bin/env python3
"""
Status reporting utilities for Zellij remote layouts.
"""

import logging
from typing import Dict, Any
from machineconfig.cluster.sessions_managers.zellij_utils.process_monitor import ProcessMonitor
from machineconfig.cluster.sessions_managers.zellij_utils.session_manager import SessionManager
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

logger = logging.getLogger(__name__)


class StatusReporter:
    """Handles comprehensive status reporting for Zellij remote sessions."""

    def __init__(self, process_monitor: ProcessMonitor, session_manager: SessionManager):
        self.process_monitor = process_monitor
        self.session_manager = session_manager

    def get_comprehensive_status(self, layout_config: LayoutConfig) -> Dict[str, Any]:
        """Get comprehensive status including Zellij session and all commands."""
        zellij_status = self.session_manager.check_zellij_session_status()
        commands_status = self.process_monitor.check_all_commands_status(layout_config)

        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)

        return {
            "zellij_session": zellij_status,
            "commands": commands_status,
            "summary": {
                "total_commands": total_count,
                "running_commands": running_count,
                "stopped_commands": total_count - running_count,
                "session_healthy": zellij_status.get("session_exists", False),
                "remote": self.session_manager.remote_executor.remote_name,
            },
        }

    def print_status_report(self, layout_config: LayoutConfig) -> None:
        """Print a formatted status report to console."""
        status = self.get_comprehensive_status(layout_config)
        remote_name = self.session_manager.remote_executor.remote_name
        session_name = self.session_manager.session_name

        print("=" * 60)
        print(f"🔍 ZELLIJ REMOTE LAYOUT STATUS REPORT ({remote_name})")
        print("=" * 60)

        # Zellij session status
        zellij = status["zellij_session"]
        if zellij.get("zellij_running", False):
            if zellij.get("session_exists", False):
                print(f"✅ Zellij session '{session_name}' is running on {remote_name}")
            else:
                print(f"⚠️  Zellij is running on {remote_name} but session '{session_name}' not found")
        else:
            print(f"❌ Zellij session issue on {remote_name}: {zellij.get('error', 'Unknown error')}")

        print()

        # Commands status
        print("📋 COMMAND STATUS:")
        print("-" * 40)

        for tab_name, cmd_status in status["commands"].items():
            if cmd_status.get("running", False):
                print(f"✅ {tab_name}: Running on {remote_name}")
                if cmd_status.get("processes"):
                    for proc in cmd_status["processes"][:2]:  # Show first 2 processes
                        print(f"   └─ PID {proc['pid']}: {proc['name']} ({proc['status']})")
            else:
                print(f"❌ {tab_name}: Not running on {remote_name}")
            print(f"   Command: {cmd_status.get('command', 'Unknown')}")
            print()

        # Summary
        summary = status["summary"]
        print("📊 SUMMARY:")
        print(f"   Remote machine: {remote_name}")
        print(f"   Total commands: {summary['total_commands']}")
        print(f"   Running: {summary['running_commands']}")
        print(f"   Stopped: {summary['stopped_commands']}")
        print(f"   Session healthy: {'✅' if summary['session_healthy'] else '❌'}")
        print("=" * 60)
