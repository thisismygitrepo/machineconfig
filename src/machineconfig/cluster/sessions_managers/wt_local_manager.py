#!/usr/bin/env python3
from datetime import datetime
import json
import uuid
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from machineconfig.utils.utils5 import Scheduler
from machineconfig.cluster.sessions_managers.wt_local import WTLayoutGenerator
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TMP_SERIALIZATION_DIR = Path.home().joinpath("tmp_results", "session_manager", "wt", "local_manager")


class WTLocalManager:
    """Manages multiple local Windows Terminal sessions and monitors their tabs and processes."""

    def __init__(self, session_layouts: list[LayoutConfig], session_name_prefix: str = "LocalWTMgr"):
        """
        Initialize the local Windows Terminal manager.

        Args:
            session_layouts: Dict mapping session names to their layout configs
                Format: {session_name: LayoutConfig, ...}
            session_name_prefix: Prefix for session names
        """
        self.session_name_prefix = session_name_prefix
        self.session_layouts = session_layouts  # Store the original config
        self.managers: List[WTLayoutGenerator] = []

        # Create a WTLayoutGenerator for each session
        for layout_config in session_layouts:
            manager = WTLayoutGenerator()
            manager.create_wt_layout(layout_config=layout_config, output_dir=None)
            self.managers.append(manager)

        logger.info(f"Initialized WTLocalManager with {len(self.managers)} sessions")

    def get_all_session_names(self) -> List[str]:
        """Get all managed session names."""
        return [manager.session_name for manager in self.managers if manager.session_name is not None]

    def start_all_sessions(self) -> Dict[str, Any]:
        """Start all Windows Terminal sessions with their layouts."""
        results = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                script_path = manager.script_path

                if not script_path:
                    results[session_name] = {"success": False, "error": "No script file path available"}
                    continue

                # Execute the PowerShell script to start Windows Terminal
                cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}"'

                logger.info(f"Starting session '{session_name}' with script: {script_path}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    results[session_name] = {"success": True, "message": f"Session '{session_name}' started successfully"}
                    logger.info(f"✅ Session '{session_name}' started successfully")
                else:
                    results[session_name] = {"success": False, "error": result.stderr or result.stdout}
                    logger.error(f"❌ Failed to start session '{session_name}': {result.stderr}")

            except Exception as e:
                results[session_name] = {"success": False, "error": str(e)}
                logger.error(f"❌ Exception starting session '{session_name}': {e}")

        return results

    def kill_all_sessions(self) -> Dict[str, Any]:
        """Kill all managed Windows Terminal sessions."""
        results = {}
        for manager in self.managers:
            session_name = manager.session_name or "unknown"
            try:
                # Kill all Windows Terminal processes (Windows Terminal doesn't have session-specific killing)
                cmd = "powershell -Command \"Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force\""

                logger.info(f"Killing Windows Terminal processes for session '{session_name}'")
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

    def check_all_sessions_status(self) -> Dict[str, Dict[str, Any]]:
        """Check the status of all sessions and their commands."""
        status_report = {}

        for manager in self.managers:
            session_name = manager.session_name or "default"

            # Get session status
            session_status = WTLayoutGenerator.check_wt_session_status(session_name)

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

    def get_global_summary(self) -> Dict[str, Any]:
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
        print("🖥️  WINDOWS TERMINAL LOCAL MANAGER STATUS REPORT")
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

            print(f"🪟 SESSION: {session_name}")
            print("-" * 60)

            # Session health
            if session_status.get("wt_running", False):
                if session_status.get("session_exists", False):
                    session_windows = session_status.get("session_windows", [])
                    all_windows = session_status.get("all_windows", [])
                    print("✅ Windows Terminal is running")
                    print(f"   Session windows: {len(session_windows)}")
                    print(f"   Total WT windows: {len(all_windows)}")
                else:
                    print("⚠️  Windows Terminal is running but no session windows found")
            else:
                print(f"❌ Windows Terminal session issue: {session_status.get('error', 'Unknown error')}")

            # Commands in this session
            print(f"   Commands ({summary['running_commands']}/{summary['total_commands']} running):")
            for tab_name, cmd_status in commands_status.items():
                status_icon = "✅" if cmd_status.get("running", False) else "❌"
                cmd_text = cmd_status.get("command", "Unknown")[:50]
                if len(cmd_status.get("command", "")) > 50:
                    cmd_text += "..."
                print(f"     {status_icon} {tab_name}: {cmd_text}")

                if cmd_status.get("processes"):
                    for proc in cmd_status["processes"][:2]:  # Show first 2 processes
                        print(f"        └─ PID {proc['pid']}: {proc['name']}")
            print()

        print("=" * 80)

    def run_monitoring_routine(self, wait_ms: int = 30000) -> None:
        """
        Run a continuous monitoring routine that checks status periodically.

        Args:
            wait_ms: How long to wait between checks in milliseconds (default: 30000ms = 30s)
        """

        def routine(scheduler: Scheduler):
            print(f"\n⏰ Monitoring cycle {scheduler.cycle} at {datetime.now()}")
            print("-" * 50)

            if scheduler.cycle % 2 == 0:
                # Detailed status check every other cycle
                all_status = self.check_all_sessions_status()

                # Create DataFrame-like data for easier viewing
                status_data = []
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
                    headers = ["session", "tab", "running", "command", "processes"]
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
                        scheduler.max_cycles = scheduler.cycle
                        return
                else:
                    print("No status data available")
            else:
                # Quick summary check
                global_summary = self.get_global_summary()
                print(f"📊 Quick Summary: {global_summary['running_commands']}/{global_summary['total_commands']} commands running across {global_summary['healthy_sessions']}/{global_summary['total_sessions']} sessions")

        logger.info(f"Starting monitoring routine with {wait_ms}ms intervals")
        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=logger)
        sched.run(max_cycles=None)

    def save(self, session_id: Optional[str] = None) -> str:
        """Save the manager state to disk."""
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]

        # Create session directory
        session_dir = TMP_SERIALIZATION_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save the session2wt_tabs configuration
        config_file = session_dir / "session_layouts.json"
        text = json.dumps(self.session_layouts, indent=2, ensure_ascii=False)
        config_file.write_text(text, encoding="utf-8")

        # Save metadata
        metadata = {"session_name_prefix": self.session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(self.managers), "sessions": [item["layoutName"] for item in self.session_layouts], "manager_type": "WTLocalManager"}
        metadata_file = session_dir / "metadata.json"
        text = json.dumps(metadata, indent=2, ensure_ascii=False)
        metadata_file.write_text(text, encoding="utf-8")

        # Save each manager's state
        managers_dir = session_dir / "managers"
        managers_dir.mkdir(exist_ok=True)

        for i, manager in enumerate(self.managers):
            manager_data = {"session_name": manager.session_name, "layout_config": manager.layout_config, "script_path": manager.script_path}
            manager_file = managers_dir / f"manager_{i}_{manager.session_name}.json"
            text = json.dumps(manager_data, indent=2, ensure_ascii=False)
            manager_file.write_text(text, encoding="utf-8")

        logger.info(f"✅ Saved WTLocalManager session to: {session_dir}")
        return session_id

    @classmethod
    def load(cls, session_id: str) -> "WTLocalManager":
        """Load a saved manager state from disk."""
        session_dir = TMP_SERIALIZATION_DIR / session_id

        if not session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")

        # Load configuration
        config_file = session_dir / "session_layouts.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        text = config_file.read_text(encoding="utf-8")
        session_layouts = json.loads(text)

        # Load metadata
        metadata_file = session_dir / "metadata.json"
        session_name_prefix = "LocalWTMgr"  # default fallback
        if metadata_file.exists():
            text = metadata_file.read_text(encoding="utf-8")
            metadata = json.loads(text)
            session_name_prefix = metadata.get("session_name_prefix", "LocalWTMgr")

        # Create new instance
        instance = cls(session_layouts=session_layouts, session_name_prefix=session_name_prefix)

        # Load saved manager states
        managers_dir = session_dir / "managers"
        if managers_dir.exists():
            instance.managers = []
            manager_files = sorted(managers_dir.glob("manager_*.json"))

            for manager_file in manager_files:
                try:
                    text = manager_file.read_text(encoding="utf-8")
                    manager_data = json.loads(text)

                    # Recreate the manager
                    manager = WTLayoutGenerator()
                    manager.session_name = manager_data["session_name"]
                    manager.layout_config = manager_data["layout_config"]
                    manager.script_path = manager_data["script_path"]

                    instance.managers.append(manager)

                except Exception as e:
                    logger.warning(f"Failed to load manager from {manager_file}: {e}")

        logger.info(f"✅ Loaded WTLocalManager session from: {session_dir}")
        return instance

    @staticmethod
    def list_saved_sessions() -> List[str]:
        """List all saved session IDs."""
        if not TMP_SERIALIZATION_DIR.exists():
            return []

        sessions = []
        for item in TMP_SERIALIZATION_DIR.iterdir():
            if item.is_dir() and (item / "metadata.json").exists():
                sessions.append(item.name)

        return sorted(sessions)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a saved session."""
        session_dir = TMP_SERIALIZATION_DIR / session_id

        if not session_dir.exists():
            logger.warning(f"Session directory not found: {session_dir}")
            return False

        try:
            import shutil

            shutil.rmtree(session_dir)
            logger.info(f"✅ Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List currently active Windows Terminal sessions managed by this instance."""
        active_sessions = []

        try:
            # Get all running Windows Terminal processes
            result = subprocess.run(
                ["powershell", "-Command", 'Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle | ConvertTo-Json -Depth 2'], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                import json

                all_processes = json.loads(result.stdout.strip())
                if not isinstance(all_processes, list):
                    all_processes = [all_processes]

                # Filter to only our managed sessions
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
                            "windows": session_windows,
                        }
                    )

        except Exception as e:
            logger.error(f"Error listing active sessions: {e}")

        return active_sessions

    def get_wt_overview(self) -> Dict[str, Any]:
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
                {"tabName": "🚀Frontend", "startDir": "~/code/myapp/frontend", "command": "npm run dev"},
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
