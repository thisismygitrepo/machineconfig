from datetime import datetime
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, Any
from machineconfig.utils.utils5 import Scheduler
from machineconfig.cluster.sessions_managers.wt_local import run_command_in_wt_tab
from machineconfig.cluster.sessions_managers.wt_remote import WTRemoteLayoutGenerator
from machineconfig.utils.schemas.layouts.layout_types import TabConfig

TMP_SERIALIZATION_DIR = Path.home().joinpath("tmp_results", "session_manager", "wt", "remote_manager")

# Module-level logger to be used throughout this module
logger = logging.getLogger(__name__)


class WTSessionManager:
    def __init__(self, machine2wt_tabs: dict[str, dict[str, tuple[str, str]]], session_name_prefix: str = "WTJobMgr"):
        self.session_name_prefix = session_name_prefix
        self.machine2wt_tabs = machine2wt_tabs  # Store the original config
        self.managers: list[WTRemoteLayoutGenerator] = []
        for machine, tab_config in machine2wt_tabs.items():
            an_m = WTRemoteLayoutGenerator(remote_name=machine, session_name_prefix=self.session_name_prefix)
            # Convert legacy dict[str, tuple[str,str]] to List[TabConfig]
            tabs: list[TabConfig] = [{"tabName": name, "startDir": cwd, "command": cmd} for name, (cwd, cmd) in tab_config.items()]
            an_m.create_wt_layout(tabs=tabs, output_dir=None)
            self.managers.append(an_m)

    def ssh_to_all_machines(self) -> str:
        hostname2wt_session = {}
        for an_m in self.managers:
            hostname = an_m.remote_name
            session_name = an_m.session_name
            hostname2wt_session[hostname] = session_name
        cmds = ""
        for hostname, session_name in hostname2wt_session.items():
            # ssh hpc-node024 -t "wt -w WTJobMgrd074muex"
            ssh_cmd = f"ssh {hostname} -t 'wt -w {session_name}'"
            a_cmd = run_command_in_wt_tab(command=ssh_cmd, tab_name=hostname, cwd=None)
            cmds += a_cmd + "\n"
        return cmds

    def kill_all_sessions(self) -> None:
        for an_m in self.managers:
            an_m.remote_executor.run_command("powershell -Command \"Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force\"")

    def run_monitoring_routine(self, wait_ms: int = 60000) -> None:
        def routine(scheduler: Scheduler):
            if scheduler.cycle % 2 == 0:
                statuses = []
                for _idx, an_m in enumerate(self.managers):
                    a_status = an_m.process_monitor.check_all_commands_status(an_m.tabs)
                    statuses.append(a_status)
                keys = []
                for item in statuses:
                    keys.extend(item.keys())
                values = []
                for item in statuses:
                    values.extend(item.values())
                # Create list of dictionaries instead of DataFrame
                status_data = []
                for i, key in enumerate(keys):
                    if i < len(values):
                        status_data.append({"tabName": key, "status": values[i]})

                # Check if all stopped
                running_count = sum(1 for item in status_data if item.get("status", {}).get("running", False))
                if running_count == 0:  # they all stopped
                    scheduler.max_cycles = scheduler.cycle  # stop the scheduler from calling this routine again

                # Print status
                for item in status_data:
                    print(f"Tab: {item['tabName']}, Status: {item['status']}")
            else:
                statuses = []
                for _idx, an_m in enumerate(self.managers):
                    a_status = an_m.session_manager.check_wt_session_status()
                    statuses.append(a_status)

                # Print statuses
                for i, status in enumerate(statuses):
                    print(f"Manager {i}: {status}")

        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=logger)
        sched.run()

    def save(self, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]

        # Create session directory
        session_dir = TMP_SERIALIZATION_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save the machine2wt_tabs configuration
        config_file = session_dir / "machine2wt_tabs.json"
        text = json.dumps(self.machine2wt_tabs, indent=2, ensure_ascii=False)
        config_file.write_text(text, encoding="utf-8")

        # Save session metadata
        metadata = {"session_name_prefix": self.session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(self.managers), "machines": list(self.machine2wt_tabs.keys()), "manager_type": "WTSessionManager"}
        metadata_file = session_dir / "metadata.json"
        text = json.dumps(metadata, indent=2, ensure_ascii=False)
        metadata_file.write_text(text, encoding="utf-8")

        # Save each WTRemoteLayoutGenerator
        managers_dir = session_dir / "managers"
        managers_dir.mkdir(exist_ok=True)

        for i, manager in enumerate(self.managers):
            manager_file = managers_dir / f"manager_{i}_{manager.remote_name}.json"
            manager.to_json(str(manager_file))

        logger.info(f"✅ Saved WTSessionManager session to: {session_dir}")
        return session_id

    @classmethod
    def load(cls, session_id: str) -> "WTSessionManager":
        session_dir = TMP_SERIALIZATION_DIR / session_id

        if not session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        config_file = session_dir / "machine2wt_tabs.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        text = config_file.read_text(encoding="utf-8")
        machine2wt_tabs = json.loads(text)

        # Load metadata
        metadata_file = session_dir / "metadata.json"
        session_name_prefix = "WTJobMgr"  # default fallback
        if metadata_file.exists():
            text = metadata_file.read_text(encoding="utf-8")
            metadata = json.loads(text)
            session_name_prefix = metadata.get("session_name_prefix", "WTJobMgr")
        # Create new instance (this will create new managers)
        instance = cls(machine2wt_tabs=machine2wt_tabs, session_name_prefix=session_name_prefix)
        # Load saved managers to restore their states
        managers_dir = session_dir / "managers"
        if managers_dir.exists():
            # Clear the auto-created managers and load the saved ones
            instance.managers = []
            # Get all manager files and sort them
            manager_files = sorted(managers_dir.glob("manager_*.json"))
            for manager_file in manager_files:
                try:
                    loaded_manager = WTRemoteLayoutGenerator.from_json(str(manager_file))
                    instance.managers.append(loaded_manager)
                except Exception as e:
                    logger.warning(f"Failed to load manager from {manager_file}: {e}")
        logger.info(f"✅ Loaded WTSessionManager session from: {session_dir}")
        return instance

    @staticmethod
    def list_saved_sessions() -> list[str]:
        if not TMP_SERIALIZATION_DIR.exists():
            return []

        sessions = []
        for item in TMP_SERIALIZATION_DIR.iterdir():
            if item.is_dir() and (item / "metadata.json").exists():
                sessions.append(item.name)

        return sorted(sessions)

    @staticmethod
    def delete_session(session_id: str) -> bool:
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

    def start_all_sessions(self) -> dict[str, Any]:
        """Start all Windows Terminal sessions on their respective remote machines."""
        results = {}
        for manager in self.managers:
            try:
                session_name = manager.session_name
                remote_name = manager.remote_name

                # Start the Windows Terminal session on the remote machine
                start_result = manager.session_manager.start_wt_session(manager.script_path)

                results[f"{remote_name}:{session_name}"] = start_result

                if start_result.get("success"):
                    logger.info(f"✅ Started session '{session_name}' on {remote_name}")
                else:
                    logger.error(f"❌ Failed to start session '{session_name}' on {remote_name}: {start_result.get('error')}")

            except Exception as e:
                results[f"{manager.remote_name}:{manager.session_name}"] = {"success": False, "error": str(e)}
                logger.error(f"❌ Exception starting session on {manager.remote_name}: {e}")

        return results

    def check_all_sessions_status(self) -> dict[str, dict[str, Any]]:
        """Check the status of all remote sessions and their commands."""
        status_report = {}

        for manager in self.managers:
            session_key = f"{manager.remote_name}:{manager.session_name}"

            try:
                # Get Windows Terminal session status
                wt_status = manager.session_manager.check_wt_session_status()

                # Get commands status for this session
                commands_status = manager.process_monitor.check_all_commands_status(manager.tabs)

                # Calculate summary for this session
                running_count = sum(1 for status in commands_status.values() if status.get("running", False))
                total_count = len(commands_status)

                status_report[session_key] = {
                    "remote_name": manager.remote_name,
                    "session_name": manager.session_name,
                    "wt_status": wt_status,
                    "commands_status": commands_status,
                    "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": wt_status.get("wt_running", False)},
                }

            except Exception as e:
                status_report[session_key] = {"remote_name": manager.remote_name, "session_name": manager.session_name, "error": str(e), "summary": {"total_commands": 0, "running_commands": 0, "stopped_commands": 0, "session_healthy": False}}
                logger.error(f"Error checking status for {session_key}: {e}")

        return status_report

    def get_global_summary(self) -> dict[str, Any]:
        """Get a global summary across all remote sessions."""
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
            "remote_machines": list(set(status["remote_name"] for status in all_status.values())),
        }

    def print_status_report(self) -> None:
        """Print a comprehensive status report for all remote sessions."""
        all_status = self.check_all_sessions_status()
        global_summary = self.get_global_summary()

        print("=" * 80)
        print("🖥️  WINDOWS TERMINAL REMOTE MANAGER STATUS REPORT")
        print("=" * 80)

        # Global summary
        print("🌐 GLOBAL SUMMARY:")
        print(f"   Total sessions: {global_summary['total_sessions']}")
        print(f"   Healthy sessions: {global_summary['healthy_sessions']}")
        print(f"   Total commands: {global_summary['total_commands']}")
        print(f"   Running commands: {global_summary['running_commands']}")
        print(f"   Remote machines: {len(global_summary['remote_machines'])}")
        print(f"   All healthy: {'✅' if global_summary['all_sessions_healthy'] else '❌'}")
        print()

        # Per-session details
        for _, status in all_status.items():
            remote_name = status["remote_name"]
            session_name = status["session_name"]

            print(f"🖥️  REMOTE: {remote_name} | SESSION: {session_name}")
            print("-" * 60)

            if "error" in status:
                print(f"❌ Error: {status['error']}")
                print()
                continue

            wt_status = status["wt_status"]
            commands_status = status["commands_status"]
            summary = status["summary"]

            # Windows Terminal session health
            if wt_status.get("wt_running", False):
                if wt_status.get("session_exists", False):
                    session_windows = wt_status.get("session_windows", [])
                    all_windows = wt_status.get("all_windows", [])
                    print(f"✅ Windows Terminal is running on {remote_name}")
                    print(f"   Session windows: {len(session_windows)}")
                    print(f"   Total WT windows: {len(all_windows)}")
                else:
                    print(f"⚠️  Windows Terminal is running but no session windows found on {remote_name}")
            else:
                print(f"❌ Windows Terminal issue on {remote_name}: {wt_status.get('error', 'Unknown error')}")

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
                        print(f"        └─ PID {proc.get('pid', 'Unknown')}: {proc.get('name', 'Unknown')}")
            print()

        print("=" * 80)

    def get_remote_overview(self) -> dict[str, Any]:
        """Get overview of all remote machines and their Windows Terminal status."""
        overview = {}

        for manager in self.managers:
            try:
                remote_name = manager.remote_name

                # Get remote Windows info
                windows_info = manager.remote_executor.get_remote_windows_info()

                # Get Windows Terminal processes
                wt_processes = manager.remote_executor.list_wt_processes()

                # Get Windows Terminal version
                wt_version = manager.session_manager.get_wt_version()

                overview[remote_name] = {"windows_info": windows_info, "wt_processes": wt_processes, "wt_version": wt_version, "session_name": manager.session_name, "tab_count": len(manager.tabs)}

            except Exception as e:
                overview[manager.remote_name] = {"error": str(e), "session_name": manager.session_name}

        return overview

    def print_remote_overview(self) -> None:
        """Print overview of all remote machines."""
        overview = self.get_remote_overview()

        print("=" * 80)
        print("🌐 REMOTE MACHINES OVERVIEW")
        print("=" * 80)

        for remote_name, info in overview.items():
            print(f"🖥️  REMOTE: {remote_name}")
            print("-" * 40)

            if "error" in info:
                print(f"❌ Error: {info['error']}")
                print()
                continue

            # Windows Terminal availability
            windows_info = info.get("windows_info", {})
            wt_available = windows_info.get("wt_available", False)
            print(f"Windows Terminal: {'✅ Available' if wt_available else '❌ Not Available'}")

            # Version info
            wt_version = info.get("wt_version", {})
            if wt_version.get("success"):
                print(f"Version: {wt_version.get('version', 'Unknown')}")

            # Current processes
            wt_processes = info.get("wt_processes", {})
            if wt_processes.get("success"):
                processes_output = wt_processes.get("processes", "")
                if processes_output.strip():
                    print("Active processes: Found")
                else:
                    print("Active processes: None")

            # Session info
            session_name = info.get("session_name", "Unknown")
            tab_count = info.get("tab_count", 0)
            print(f"Managed session: {session_name} ({tab_count} tabs)")

            print()

        print("=" * 80)


if __name__ == "__main__":
    # Example usage
    sample_machines = {
        "server1": {"🤖Bot1": ("~/code/project", "python bot1.py"), "📊Monitor": ("~", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10")},
        "server2": {"🤖Bot2": ("~/code/project", "python bot2.py"), "📝Logs": ("C:/logs", "Get-Content app.log -Wait")},
    }

    try:
        # Create the remote manager
        manager = WTSessionManager(sample_machines, session_name_prefix="RemoteJobs")
        print(f"✅ Remote manager created with {len(manager.managers)} remote sessions")

        # Show SSH commands
        print("\n📎 SSH commands to connect to all machines:")
        ssh_commands = manager.ssh_to_all_machines()
        print(ssh_commands)

        # Show current status
        print("\n🔍 Current status:")
        manager.print_status_report()

        # Show remote overview
        print("\n🌐 Remote machines overview:")
        manager.print_remote_overview()

        # Demonstrate save/load
        print("\n💾 Demonstrating save/load...")
        session_id = manager.save()
        print(f"✅ Saved session: {session_id}")

        # List saved sessions
        saved_sessions = WTSessionManager.list_saved_sessions()
        print(f"📋 Saved sessions: {saved_sessions}")

        # Load and verify
        loaded_manager = WTSessionManager.load(session_id)
        print(f"✅ Loaded session with {len(loaded_manager.managers)} remote sessions")

        # Show how to start sessions
        print("\n▶️  To start all sessions, run:")
        print("manager.start_all_sessions()")

        # Show how to start monitoring (commented out to prevent infinite loop in demo)
        print("\n⏰ To start monitoring, run:")
        print("manager.run_monitoring_routine(wait_ms=60000)  # 60 seconds")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
