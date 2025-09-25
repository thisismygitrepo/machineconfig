from datetime import datetime
import json
import uuid
from pathlib import Path
from typing import Optional, Dict
from machineconfig.utils.utils5 import Scheduler
from machineconfig.cluster.sessions_managers.zellij_local import run_command_in_zellij_tab
from machineconfig.cluster.sessions_managers.zellij_remote import ZellijRemoteLayoutGenerator
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.logger import get_logger


TMP_SERIALIAZATION_DIR = Path.home().joinpath("tmp_results", "session_manager", "zellij", "remote_manager")
logger = get_logger("cluster.sessions_managers.zellij_remote_manager")


class ZellijSessionManager:
    def __init__(self, machine_layouts: Dict[str, LayoutConfig], session_name_prefix: str):
        self.session_name_prefix = session_name_prefix
        self.machine_layouts = machine_layouts  # Store the original config
        self.managers: list[ZellijRemoteLayoutGenerator] = []
        for machine, layout_config in machine_layouts.items():
            an_m = ZellijRemoteLayoutGenerator(remote_name=machine, session_name_prefix=self.session_name_prefix)
            an_m.create_zellij_layout(layout_config=layout_config, output_dir=None)
            self.managers.append(an_m)

    def ssh_to_all_machines(self) -> str:
        hostname2zellij_session = {}
        for an_m in self.managers:
            hostname = an_m.remote_name
            session_name = an_m.session_name
            hostname2zellij_session[hostname] = session_name
        cmds = ""
        for hostname, session_name in hostname2zellij_session.items():
            # ssh hpc-node024 -t "zellij attach JobMgrd074muex"
            ssh_cmd = f"ssh {hostname} -t 'zellij attach {session_name}'"
            a_cmd = run_command_in_zellij_tab(command=ssh_cmd, tab_name=hostname, cwd=None)
            cmds += a_cmd + "\n"
        return cmds

    def kill_all_sessions(self) -> None:
        for an_m in self.managers:
            ZellijRemoteLayoutGenerator.run_remote_command(remote_name=an_m.remote_name, command="zellij kill-all-sessions --yes", timeout=30)

    def start_zellij_sessions(self) -> None:
        for an_m in self.managers:
            an_m.session_manager.start_zellij_session(an_m.layout_path)

    def run_monitoring_routine(self) -> None:
        def routine(scheduler: Scheduler):
            if scheduler.cycle % 2 == 0:
                statuses = []
                for _idx, an_m in enumerate(self.managers):
                    if not an_m.layout_config:
                        a_status = {}
                    else:
                        a_status = an_m.process_monitor.check_all_commands_status(an_m.layout_config)
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
                    sched.max_cycles = sched.cycle  # stop the scheduler from calling this routine again

                # Print status
                for item in status_data:
                    print(f"Tab: {item['tabName']}, Status: {item['status']}")
            else:
                statuses = []
                for _idx, an_m in enumerate(self.managers):
                    a_status = an_m.session_manager.check_zellij_session_status()
                    statuses.append(a_status)

                # Print statuses
                for i, status in enumerate(statuses):
                    print(f"Manager {i}: {status}")

        sched = Scheduler(routine=routine, wait_ms=60_000, logger=logger)
        sched.run()

    def save(self, session_id: Optional[str]) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]

        # Create session directory
        session_dir = TMP_SERIALIAZATION_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save the machine_layouts configuration
        config_file = session_dir / "machine_layouts.json"
        text = json.dumps(self.machine_layouts, indent=2, ensure_ascii=False)
        config_file.write_text(text, encoding="utf-8")

        # Save session metadata
        metadata = {"session_name_prefix": self.session_name_prefix, "created_at": str(datetime.now()), "num_managers": len(self.managers), "machines": list(self.machine_layouts.keys())}
        metadata_file = session_dir / "metadata.json"
        text = json.dumps(metadata, indent=2, ensure_ascii=False)
        metadata_file.write_text(text, encoding="utf-8")

        # Save each ZellijRemoteLayoutGenerator
        managers_dir = session_dir / "managers"
        managers_dir.mkdir(exist_ok=True)

        for i, manager in enumerate(self.managers):
            manager_file = managers_dir / f"manager_{i}_{manager.remote_name}.json"
            manager.to_json(str(manager_file))
        logger.info(f"✅ Saved ZellijSessionManager session to: {session_dir}")
        return session_id

    @classmethod
    def load(cls, session_id: str) -> "ZellijSessionManager":
        session_dir = TMP_SERIALIAZATION_DIR / session_id

        if not session_dir.exists():
            raise FileNotFoundError(f"Session directory not found: {session_dir}")
        config_file = session_dir / "machine_layouts.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        text = config_file.read_text(encoding="utf-8")
        machine_layouts = json.loads(text)

        # Load metadata
        metadata_file = session_dir / "metadata.json"
        session_name_prefix = "JobMgr"  # default fallback
        if metadata_file.exists():
            text = metadata_file.read_text(encoding="utf-8")
            metadata = json.loads(text)
            session_name_prefix = metadata.get("session_name_prefix", "JobMgr")
        # Create new instance (this will create new managers)
        instance = cls(machine_layouts=machine_layouts, session_name_prefix=session_name_prefix)
        # Load saved managers to restore their states
        managers_dir = session_dir / "managers"
        if managers_dir.exists():
            # Clear the auto-created managers and load the saved ones
            instance.managers = []
            # Get all manager files and sort them
            manager_files = sorted(managers_dir.glob("manager_*.json"))
            for manager_file in manager_files:
                try:
                    loaded_manager = ZellijRemoteLayoutGenerator.from_json(str(manager_file))
                    instance.managers.append(loaded_manager)
                except Exception as e:
                    logger.warning(f"Failed to load manager from {manager_file}: {e}")
        logger.info(f"✅ Loaded ZellijSessionManager session from: {session_dir}")
        return instance

    @staticmethod
    def list_saved_sessions() -> list[str]:
        if not TMP_SERIALIAZATION_DIR.exists():
            return []

        sessions = []
        for item in TMP_SERIALIAZATION_DIR.iterdir():
            if item.is_dir() and (item / "metadata.json").exists():
                sessions.append(item.name)

        return sorted(sessions)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        session_dir = TMP_SERIALIAZATION_DIR / session_id

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
