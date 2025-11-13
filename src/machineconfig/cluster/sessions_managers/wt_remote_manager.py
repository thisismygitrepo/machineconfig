from datetime import datetime
import logging
from pathlib import Path
from typing import Optional, Any
from rich.console import Console
from machineconfig.utils.scheduler import Scheduler
from machineconfig.cluster.sessions_managers.wt_local import run_command_in_wt_tab
from machineconfig.cluster.sessions_managers.wt_remote import WTRemoteLayoutGenerator
from machineconfig.cluster.sessions_managers.wt_utils.wt_helpers import generate_random_suffix
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig
from machineconfig.cluster.sessions_managers.wt_utils.manager_persistence import (
    generate_session_id, save_json_file, load_json_file, list_saved_sessions_in_dir, delete_session_dir, ensure_session_dir_exists
)
from machineconfig.cluster.sessions_managers.wt_utils.status_reporting import (
    print_global_summary, print_session_health_status, print_commands_status, calculate_session_summary, calculate_global_summary_from_status
)
from machineconfig.cluster.sessions_managers.wt_utils.monitoring_helpers import (
    collect_status_data_from_managers, flatten_status_data, check_if_all_stopped, print_status_table, collect_session_statuses, print_session_statuses
)


# Module-level logger to be used throughout this module
logger = logging.getLogger(__name__)
console = Console()
TMP_SERIALIZATION_DIR = Path.home() / "tmp_results" / "wt_sessions" / "serialized"


class WTSessionManager:
    def __init__(self, machine2wt_tabs: dict[str, dict[str, tuple[str, str]]], session_name_prefix: str = "WTJobMgr"):
        self.session_name_prefix = session_name_prefix
        self.machine2wt_tabs = machine2wt_tabs  # Store the original config
        self.managers: list[WTRemoteLayoutGenerator] = []
        for machine, tab_config in machine2wt_tabs.items():
            # Convert legacy dict[str, tuple[str,str]] to LayoutConfig
            tabs: list[TabConfig] = [{"tabName": name, "startDir": cwd, "command": cmd} for name, (cwd, cmd) in tab_config.items()]
            layout_config: LayoutConfig = {"layoutName": f"{session_name_prefix}_{machine}", "layoutTabs": tabs}
            session_name = f"{session_name_prefix}_{generate_random_suffix(8)}"
            an_m = WTRemoteLayoutGenerator(layout_config=layout_config, remote_name=machine, session_name=session_name)
            an_m.create_layout_file()
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
                statuses = collect_status_data_from_managers(self.managers)
                status_data = flatten_status_data(statuses)
                if check_if_all_stopped(status_data):
                    scheduler.max_cycles = scheduler.cycle
                print_status_table(status_data)
            else:
                statuses = collect_session_statuses(self.managers)
                print_session_statuses(statuses)
        from machineconfig.utils.scheduler import LoggerTemplate
        from typing import cast
        sched = Scheduler(routine=routine, wait_ms=wait_ms, logger=cast(LoggerTemplate, logger))
        sched.run()

    def save(self, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = generate_session_id()
        session_dir = TMP_SERIALIZATION_DIR / session_id
        ensure_session_dir_exists(session_dir)
        save_json_file(session_dir / "machine2wt_tabs.json", self.machine2wt_tabs, "machine2wt_tabs")
        metadata = {"session_name_prefix": self.session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(self.managers), "machines": list(self.machine2wt_tabs.keys()), "manager_type": "WTSessionManager"}
        save_json_file(session_dir / "metadata.json", metadata, "metadata")
        managers_dir = session_dir / "managers"
        managers_dir.mkdir(exist_ok=True)
        for i, manager in enumerate(self.managers):
            manager.to_json(str(managers_dir / f"manager_{i}_{manager.remote_name}.json"))
        logger.info(f"✅ Saved WTSessionManager session to: {session_dir}")
        return session_id

    @classmethod
    def load(cls, session_id: str) -> "WTSessionManager":
        session_dir = TMP_SERIALIZATION_DIR / session_id
        if not session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        loaded_data = load_json_file(session_dir / "machine2wt_tabs.json", "Configuration file")
        machine2wt_tabs = loaded_data if isinstance(loaded_data, dict) else {}  # type: ignore[arg-type]
        metadata_data = load_json_file(session_dir / "metadata.json", "Metadata file") if (session_dir / "metadata.json").exists() else {}
        metadata = metadata_data if isinstance(metadata_data, dict) else {}  # type: ignore[arg-type]
        session_name_prefix = metadata.get("session_name_prefix", "WTJobMgr")  # type: ignore[union-attr]
        instance = cls(machine2wt_tabs=machine2wt_tabs, session_name_prefix=session_name_prefix)
        managers_dir = session_dir / "managers"
        if managers_dir.exists():
            instance.managers = []
            for manager_file in sorted(managers_dir.glob("manager_*.json")):
                try:
                    loaded_manager = WTRemoteLayoutGenerator.from_json(str(manager_file))
                    instance.managers.append(loaded_manager)
                except Exception as e:
                    logger.warning(f"Failed to load manager from {manager_file}: {e}")
        logger.info(f"✅ Loaded WTSessionManager session from: {session_dir}")
        return instance

    @staticmethod
    def list_saved_sessions() -> list[str]:
        return list_saved_sessions_in_dir(TMP_SERIALIZATION_DIR)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        return delete_session_dir(TMP_SERIALIZATION_DIR / session_id, session_id)

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
        status_report = {}
        for manager in self.managers:
            session_key = f"{manager.remote_name}:{manager.session_name}"
            try:
                wt_status = manager.session_manager.check_wt_session_status()
                tabs = manager.layout_config["layoutTabs"]
                commands_status = manager.process_monitor.check_all_commands_status(tabs)
                summary = calculate_session_summary(commands_status, wt_status.get("wt_running", False))
                status_report[session_key] = {"remote_name": manager.remote_name, "session_name": manager.session_name, "wt_status": wt_status, "commands_status": commands_status, "summary": summary}
            except Exception as e:
                status_report[session_key] = {"remote_name": manager.remote_name, "session_name": manager.session_name, "error": str(e), "summary": {"total_commands": 0, "running_commands": 0, "stopped_commands": 0, "session_healthy": False}}
                logger.error(f"Error checking status for {session_key}: {e}")
        return status_report

    def get_global_summary(self) -> dict[str, Any]:
        all_status = self.check_all_sessions_status()
        return calculate_global_summary_from_status(all_status, include_remote_machines=True)

    def print_status_report(self) -> None:
        all_status = self.check_all_sessions_status()
        global_summary = self.get_global_summary()
        print_global_summary(global_summary, "WINDOWS TERMINAL REMOTE MANAGER STATUS REPORT")
        for _, status in all_status.items():
            print(f"🖥️  REMOTE: {status['remote_name']} | SESSION: {status['session_name']}")
            print("-" * 60)
            if "error" in status:
                print(f"❌ Error: {status['error']}")
                print()
                continue
            print_session_health_status(status["wt_status"], remote_name=status["remote_name"])
            print_commands_status(status["commands_status"], status["summary"])
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

                overview[remote_name] = {"windows_info": windows_info, "wt_processes": wt_processes, "wt_version": wt_version, "session_name": manager.session_name, "tab_count": len(manager.layout_config["layoutTabs"])}

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
