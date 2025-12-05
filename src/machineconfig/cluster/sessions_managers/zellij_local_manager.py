#!/usr/bin/env python3
from datetime import datetime
import logging
import subprocess
import time
from typing import Optional

from rich.console import Console

from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import SessionReport, GlobalSummary, StartResult, ActiveSessionInfo, StatusRow
from machineconfig.utils.scheduler import Scheduler
from machineconfig.cluster.sessions_managers.zellij_local import ZellijLayoutGenerator
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.zellij_utils import zellij_local_manager_helper as helper


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()



class ZellijLocalManager:
    """Manages multiple local zellij sessions and monitors their tabs and processes."""

    def __init__(self, session_layouts: list[LayoutConfig]):
        self.session_name_prefix = "LocalJobMgr"
        self.session_layouts = session_layouts  # Store the original config
        self.managers: list[ZellijLayoutGenerator] = []

        # Create a ZellijLayoutGenerator for each session
        for layout_config in session_layouts:
            session_name = layout_config["layoutName"].replace(" ", "_")
            full_session_name = f"{self.session_name_prefix}_{session_name}"
            manager = ZellijLayoutGenerator(layout_config=layout_config, session_name=full_session_name)
            manager.create_layout_file()
            
            self.managers.append(manager)

        # Enhanced Rich logging for initialization
        console.print(f"[bold green]🔧 Initialized ZellijLocalManager[/bold green] [dim]with[/dim] [bright_green]{len(self.managers)} sessions[/bright_green]")

    def get_all_session_names(self) -> list[str]:
        """Get all managed session names."""
        return helper.get_all_session_names(self.managers)

    def start_all_sessions(self, poll_seconds: float, poll_interval: float) -> dict[str, StartResult]:
        """Start all zellij sessions with their layouts without blocking on the interactive TUI.

        Rationale:
            Previous implementation used subprocess.run(... timeout=30) on an "attach" command
            which never returns (interactive) causing a timeout. We now:
              1. Ensure any old session is deleted (best-effort, short timeout)
              2. Launch new session in background with Popen (no wait)
              3. Poll 'zellij list-sessions' to confirm creation

        Args:
            poll_seconds: Total seconds to wait for session to appear
            poll_interval: Delay between polls
        Returns:
            Dict mapping session name to success metadata.
        """
        results: dict[str, StartResult] = {}
        for manager in self.managers:
            session_name = manager.session_name
            try:
                layout_path = manager.layout_path
                if not layout_path:
                    results[session_name] = {"success": False, "error": "No layout file path available"}
                    continue

                # 1. Best-effort delete existing session
                delete_cmd = ["zellij", "delete-session", "--force", session_name]
                try:
                    subprocess.run(delete_cmd, capture_output=True, text=True, timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout deleting session {session_name}; continuing")
                except FileNotFoundError:
                    results[session_name] = {"success": False, "error": "'zellij' executable not found in PATH"}
                    continue

                # 2. Launch new session. We intentionally do NOT wait for completion.
                # Using the same pattern as before (attach --create) but detached via env var.
                # ZELLIJ_AUTO_ATTACH=0 prevents auto-attach if compiled with that feature; harmless otherwise.
                start_cmd = ["bash", "-lc", f"ZELLIJ_AUTO_ATTACH=0 zellij --layout {layout_path} attach {session_name} --create >/dev/null 2>&1 &"]
                console.print(f"[bold cyan]🚀 Starting session[/bold cyan] [yellow]'{session_name}'[/yellow] with layout [blue]{layout_path}[/blue] (non-blocking)...")
                console.print(f"[dim]   Command: {' '.join(start_cmd)}[/dim]")
                subprocess.Popen(start_cmd)

                # 3. Poll for presence
                deadline = time.time() + poll_seconds
                appeared = False
                while time.time() < deadline:
                    list_res = subprocess.run(["zellij", "list-sessions"], capture_output=True, text=True)
                    if list_res.returncode == 0 and session_name in list_res.stdout:
                        appeared = True
                        break
                    time.sleep(poll_interval)

                if appeared:
                    results[session_name] = {"success": True, "message": f"Session '{session_name}' started"}
                    console.print(f"[bold green]✅ Session[/bold green] [yellow]'{session_name}'[/yellow] [green]is up[/green]")
                else:
                    results[session_name] = {"success": False, "error": "Session did not appear within poll window"}
                    console.print(f"[bold red]❌ Session '{session_name}' did not appear after {poll_seconds:.1f}s[/bold red]")
            except Exception as e:
                key = session_name or f"manager_{self.managers.index(manager)}"
                results[key] = {"success": False, "error": str(e)}
                logger.error(f"❌ Exception starting session '{key}': {e}")
        return results

    def kill_all_sessions(self) -> dict[str, StartResult]:
        """Kill all managed zellij sessions."""
        return helper.kill_all_sessions(self.managers)

    def attach_to_session(self, session_name: Optional[str]) -> str:
        """
        Generate command to attach to a specific session or list attachment commands for all.

        Args:
            session_name: Specific session to attach to, or None for all sessions

        Returns:
            Command string to attach to session(s)
        """
        return helper.attach_to_session(self.managers, session_name)

    def check_all_sessions_status(self) -> dict[str, SessionReport]:
        """Check the status of all sessions and their commands."""
        status_report: dict[str, SessionReport] = {}

        for manager in self.managers:
            session_name = manager.session_name

            # Get session status using the helper function
            from machineconfig.cluster.sessions_managers.zellij_utils.zellij_local_helper import check_zellij_session_status
            session_status = check_zellij_session_status(session_name)

            # Get commands status for this session
            commands_status = manager.check_all_commands_status()

            # Calculate summary for this session
            running_count = sum(1 for status in commands_status.values() if status.get("running", False))
            total_count = len(commands_status)

            status_report[session_name] = {
                "session_status": session_status,
                "commands_status": commands_status,
                "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": session_status.get("session_exists", False)},
            }

        return status_report

    def get_global_summary(self) -> GlobalSummary:
        """Get a global summary across all sessions."""
        all_status = self.check_all_sessions_status()

        total_sessions = len(all_status)
        healthy_sessions = sum(1 for status in all_status.values() if status["summary"]["session_healthy"])
        total_commands = sum(status["summary"]["total_commands"] for status in all_status.values())
        total_running = sum(status["summary"]["running_commands"] for status in all_status.values())

        return {
            "total_sessions": total_sessions,
            "healthy_sessions": healthy_sessions,
            "unhealthy_sessions": total_sessions - healthy_sessions,
            "total_commands": total_commands,
            "running_commands": total_running,
            "stopped_commands": total_commands - total_running,
            "all_sessions_healthy": healthy_sessions == total_sessions,
            "all_commands_running": total_running == total_commands,
        }

    def print_status_report(self) -> None:
        """Print a comprehensive status report for all sessions."""
        all_status = self.check_all_sessions_status()
        global_summary = self.get_global_summary()

        print("=" * 80)
        print("🔍 ZELLIJ LOCAL MANAGER STATUS REPORT")
        print("=" * 80)

        # Global summary
        print("🌐 GLOBAL SUMMARY:")
        print(f"   Total sessions: {global_summary['total_sessions']}")
        print(f"   Healthy sessions: {global_summary['healthy_sessions']}")
        print(f"   Total commands: {global_summary['total_commands']}")
        print(f"   Running commands: {global_summary['running_commands']}")
        print(f"   All healthy: {'✅' if global_summary['all_sessions_healthy'] else '❌'}")
        print()

        # Per-session details
        for session_name, status in all_status.items():
            session_status = status["session_status"]
            commands_status = status["commands_status"]
            summary = status["summary"]

            print(f"📋 SESSION: {session_name}")
            print("-" * 60)

            # Session health
            if session_status.get("session_exists", False):
                print("✅ Session is running")
            else:
                print(f"❌ Session not found: {session_status.get('error', 'Unknown error')}")

            # Commands in this session
            print(f"   Commands ({summary['running_commands']}/{summary['total_commands']} running):")
            for tab_name, cmd_status in commands_status.items():
                status_icon = "✅" if cmd_status.get("running", False) else "❌"
                print(f"     {status_icon} {tab_name}: {cmd_status.get('command', 'Unknown')}")

                if cmd_status.get("processes"):
                    for proc in cmd_status["processes"][:2]:  # Show first 2 processes
                        console.print(f"        [dim]└─[/dim] PID {proc['pid']}: {proc['name']} ({proc['status']})")
            print()

        print("=" * 80)

    def run_monitoring_routine(self, wait_ms: int) -> None:
        """
        Run a continuous monitoring routine that checks status periodically.

        Args:
            wait_ms: How long to wait between checks in milliseconds
            kill_sessions_on_completion: If True, kill all managed zellij sessions when monitoring stops
        """

        def routine(scheduler: Scheduler):
            print(f"\n⏰ Monitoring cycle {scheduler.cycle} at {datetime.now()}")
            print("-" * 50)

            if scheduler.cycle % 2 == 0:
                # Detailed status check every other cycle
                all_status = self.check_all_sessions_status()

                # Create DataFrame for easier viewing
                status_data: list[StatusRow] = []
                for session_name, status in all_status.items():
                    for tab_name, cmd_status in status["commands_status"].items():
                        status_data.append(
                            {
                                "session": session_name,
                                "tab": tab_name,
                                "running": cmd_status.get("running", False),
                                "command": cmd_status.get("command", "Unknown")[:50] + "..." if len(cmd_status.get("command", "")) > 50 else cmd_status.get("command", ""),
                                "processes": len(cmd_status.get("processes", [])),
                            }
                        )

                if status_data:
                    # Format data as table
                    if status_data:
                        # Create header
                        headers = list(status_data[0].keys()) if status_data else []
                        header_line = " | ".join(f"{h:<15}" for h in headers)
                        separator = "-" * len(header_line)
                        print(header_line)
                        print(separator)
                        for row in status_data:
                            values = [str(row.get(h, ""))[:15] for h in headers]
                            print(" | ".join(f"{v:<15}" for v in values))

                    # Check if all sessions have stopped
                    running_count = sum(1 for row in status_data if row.get("running", False))
                    if running_count == 0:
                        print("\n⚠️  All commands have stopped. Stopping monitoring.")
                        # Set max_cycles to current cycle + 1 to exit after this cycle
                        scheduler.max_cycles = scheduler.cycle + 1
                        return
                else:
                    print("No status data available")
            else:
                # Quick summary check
                global_summary = self.get_global_summary()
                print(f"📊 Quick Summary: {global_summary['running_commands']}/{global_summary['total_commands']} commands running across {global_summary['healthy_sessions']}/{global_summary['total_sessions']} sessions")

        logger.info(f"Starting monitoring routine with {wait_ms}ms intervals")
        from machineconfig.utils.scheduler import LoggerTemplate
        from typing import cast
        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=cast(LoggerTemplate, logger))
        sched.run()

    def save(self, session_id: Optional[str]) -> str:
        """Save the manager state to disk."""
        return helper.save_manager(self.session_layouts, self.managers, self.session_name_prefix, session_id)

    @classmethod
    def load(cls, session_id: str) -> "ZellijLocalManager":
        """Load a saved manager state from disk."""
        session_layouts, managers = helper.load_manager(session_id)
        instance = cls(session_layouts=session_layouts)
        instance.managers = managers
        return instance

    @staticmethod
    def list_saved_sessions() -> list[str]:
        """List all saved session IDs."""
        return helper.list_saved_sessions()

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a saved session."""
        return helper.delete_session(session_id)

    def list_active_sessions(self) -> list[ActiveSessionInfo]:
        """List currently active zellij sessions managed by this instance."""
        return helper.list_active_sessions(self.managers)


if __name__ == "__main__":
    # Example usage with new schema
    sample_sessions: list[LayoutConfig] = [
        {
            "layoutName": "Development",
            "layoutTabs": [
                {"tabName": "🚀Frontend", "startDir": "~/code/myapp/frontend", "command": "bun run dev"},
                {"tabName": "⚙️Backend", "startDir": "~/code/myapp/backend", "command": "python manage.py runserver"},
                {"tabName": "📊Monitor", "startDir": "~", "command": "htop"},
            ],
        },
        {
            "layoutName": "Testing",
            "layoutTabs": [
                {"tabName": "🧪Tests", "startDir": "~/code/myapp", "command": "pytest --watch"},
                {"tabName": "🔍Coverage", "startDir": "~/code/myapp", "command": "coverage run --source=. -m pytest"},
                {"tabName": "📝Logs", "startDir": "~/logs", "command": "tail -f app.log"},
            ],
        },
        {
            "layoutName": "Deployment",
            "layoutTabs": [
                {"tabName": "🐳Docker", "startDir": "~/code/myapp", "command": "docker-compose up"},
                {"tabName": "☸️K8s", "startDir": "~/k8s", "command": "kubectl get pods --watch"},
                {"tabName": "📈Metrics", "startDir": "~", "command": "k9s"},
            ],
        },
    ]
    try:
        # Create the local manager
        manager = ZellijLocalManager(sample_sessions)
        print(f"✅ Local manager created with {len(manager.managers)} sessions")

        # Show session names
        print(f"📋 Sessions: {manager.get_all_session_names()}")

        # Print attachment commands (without actually starting)
        print("\n📎 Attachment commands:")
        print(manager.attach_to_session(None))

        # Show current status
        print("\n🔍 Current status:")
        manager.print_status_report()

        # Demonstrate save/load
        print("\n💾 Demonstrating save/load...")
        session_id = manager.save(None)
        print(f"✅ Saved session: {session_id}")

        # List saved sessions
        saved_sessions = ZellijLocalManager.list_saved_sessions()
        print(f"📋 Saved sessions: {saved_sessions}")

        # Load and verify
        loaded_manager = ZellijLocalManager.load(session_id)
        print(f"✅ Loaded session with {len(loaded_manager.managers)} sessions")

        # Show how to start monitoring (commented out to prevent infinite loop in demo)
        print("\n⏰ To start monitoring, run:")
        print("manager.run_monitoring_routine(wait_ms=30000)  # 30 seconds")
        print("# Or with session cleanup:")
        print("manager.run_monitoring_routine(wait_ms=30000, kill_sessions_on_completion=True)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
