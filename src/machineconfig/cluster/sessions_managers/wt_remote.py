#!/usr/bin/env python3
from typing import Dict, Tuple, Optional, List, Any
from pathlib import Path
import logging
import json
import uuid
from datetime import datetime

from machineconfig.cluster.sessions_managers.wt_utils.remote_executor import WTRemoteExecutor
from machineconfig.cluster.sessions_managers.wt_utils.layout_generator import WTLayoutGenerator
from machineconfig.cluster.sessions_managers.wt_utils.process_monitor import WTProcessMonitor
from machineconfig.cluster.sessions_managers.wt_utils.session_manager import WTSessionManager
from machineconfig.cluster.sessions_managers.wt_utils.status_reporter import WTStatusReporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "wt_layouts", "layout_manager")


class WTRemoteLayoutGenerator:

    def __init__(self, remote_name: str, session_name_prefix: str):
        self.remote_name = remote_name
        self.session_name = session_name_prefix + "_" + WTLayoutGenerator.generate_random_suffix()
        self.tab_config: Dict[str, Tuple[str, str]] = {}
        self.script_path: Optional[str] = None

        # Initialize modular components
        self.remote_executor = WTRemoteExecutor(remote_name)
        self.layout_generator = WTLayoutGenerator()
        self.process_monitor = WTProcessMonitor(self.remote_executor)
        self.session_manager = WTSessionManager(self.remote_executor, self.session_name, TMP_LAYOUT_DIR)
        self.status_reporter = WTStatusReporter(self.process_monitor, self.session_manager)

    def copy_script_to_remote(self, local_script_file: Path, random_suffix: str) -> str:
        return self.session_manager.copy_script_to_remote(local_script_file, random_suffix)

    def create_wt_layout(self, tab_config: Dict[str, Tuple[str, str]], output_dir: Optional[str] = None) -> str:
        logger.info(f"Creating Windows Terminal layout with {len(tab_config)} tabs for remote '{self.remote_name}'")
        self.tab_config = tab_config.copy()
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = TMP_LAYOUT_DIR
        self.script_path = self.layout_generator.create_wt_script(tab_config, output_path, self.session_name)
        return self.script_path

    def get_layout_preview(self, tab_config: Dict[str, Tuple[str, str]]) -> str:
        return self.layout_generator.generate_wt_command(tab_config)

    def check_command_status(self, tab_name: str, use_verification: bool = True) -> Dict[str, Any]:
        return self.process_monitor.check_command_status(tab_name, self.tab_config, use_verification)

    def check_all_commands_status(self) -> Dict[str, Dict[str, Any]]:
        return self.process_monitor.check_all_commands_status(self.tab_config)

    def check_wt_session_status(self) -> Dict[str, Any]:
        return self.session_manager.check_wt_session_status()

    def get_comprehensive_status(self) -> Dict[str, Any]:
        return self.status_reporter.get_comprehensive_status(self.tab_config)

    def print_status_report(self) -> None:
        self.status_reporter.print_status_report(self.tab_config)

    def start_wt_session(self, script_file_path: Optional[str] = None) -> Dict[str, Any]:
        return self.session_manager.start_wt_session(script_file_path or self.script_path)

    def attach_to_session(self) -> None:
        self.session_manager.attach_to_session()

    # Legacy methods for backward compatibility
    def force_fresh_process_check(self, tab_name: str) -> Dict[str, Any]:
        return self.process_monitor.force_fresh_process_check(tab_name, self.tab_config)

    def verify_process_alive(self, pid: int) -> bool:
        return self.process_monitor.verify_process_alive(pid)

    def get_verified_process_status(self, tab_name: str) -> Dict[str, Any]:
        return self.process_monitor.get_verified_process_status(tab_name, self.tab_config)

    # Static methods for backward compatibility
    @staticmethod
    def run_remote_command(remote_name: str, command: str, timeout: int = 30):
        executor = WTRemoteExecutor(remote_name)
        return executor.run_command(command, timeout)

    def kill_wt_session(self, force: bool = True) -> Dict[str, Any]:
        """Kill Windows Terminal processes on the remote machine."""
        return self.session_manager.kill_wt_session(force)

    def create_new_tab(self, tab_name: str, cwd: str, command: str) -> Dict[str, Any]:
        """Create a new tab in the Windows Terminal session."""
        return self.session_manager.create_new_tab(tab_name, cwd, command, self.session_name)

    def get_wt_version(self) -> Dict[str, Any]:
        """Get Windows Terminal version information on the remote machine."""
        return self.session_manager.get_wt_version()

    def get_remote_windows_info(self) -> Dict[str, Any]:
        """Get information about the remote Windows system."""
        return self.remote_executor.get_remote_windows_info()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "remote_name": self.remote_name,
            "session_name": self.session_name,
            "tab_config": self.tab_config,
            "script_path": self.script_path,
            "created_at": datetime.now().isoformat(),
            "class_name": self.__class__.__name__
        }

    def to_json(self, file_path: Optional[str] = None) -> str:
        # Generate file path if not provided
        if file_path is None:
            random_id = str(uuid.uuid4())[:8]
            default_dir = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
            default_dir.mkdir(parents=True, exist_ok=True)
            path_obj = default_dir / f"wt_session_{random_id}.json"
        else:
            path_obj = Path(file_path)

        # Ensure .json extension
        if not str(path_obj).endswith('.json'):
            path_obj = path_obj.with_suffix('.json')

        # Ensure parent directory exists
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to JSON
        data = self.to_dict()

        text = json.dumps(data, indent=2, ensure_ascii=False)
        path_obj.write_text(text, encoding="utf-8")

        logger.info(f"✅ Serialized WTRemoteLayoutGenerator to: {path_obj}")
        return str(path_obj)

    @classmethod
    def from_json(cls, file_path: str) -> 'WTRemoteLayoutGenerator':
        path_obj = Path(file_path)

        # Ensure .json extension
        if not str(path_obj).endswith('.json'):
            path_obj = path_obj.with_suffix('.json')

        if not path_obj.exists():
            raise FileNotFoundError(f"JSON file not found: {path_obj}")

        # Load JSON data
        with open(path_obj, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate that it's the correct class
        if data.get('class_name') != cls.__name__:
            logger.warning(f"Class name mismatch: expected {cls.__name__}, got {data.get('class_name')}")

        # Create new instance
        # Extract session name prefix by removing the suffix
        session_name = data['session_name']
        if '_' in session_name:
            session_name_prefix = '_'.join(session_name.split('_')[:-1])
        else:
            session_name_prefix = session_name

        instance = cls(remote_name=data['remote_name'], session_name_prefix=session_name_prefix)

        # Restore state
        instance.session_name = data['session_name']
        instance.tab_config = data['tab_config']
        instance.script_path = data['script_path']

        logger.info(f"✅ Loaded WTRemoteLayoutGenerator from: {file_path}")
        return instance

    @staticmethod
    def list_saved_sessions(directory_path: Optional[str] = None) -> List[str]:
        if directory_path is None:
            dir_path = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
        else:
            dir_path = Path(directory_path)

        if not dir_path.exists():
            return []

        json_files = [f.name for f in dir_path.glob("*.json")]
        return sorted(json_files)

    def check_wt_available(self) -> bool:
        """Check if Windows Terminal is available on the remote machine."""
        return self.remote_executor.check_wt_available()

    def list_wt_processes(self) -> Dict[str, Any]:
        """List Windows Terminal processes on the remote machine."""
        return self.remote_executor.list_wt_processes()

    def kill_wt_processes(self, process_ids: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Kill Windows Terminal processes on the remote machine."""
        return self.remote_executor.kill_wt_processes(process_ids)

    def get_windows_terminal_overview(self) -> Dict[str, Any]:
        """Get overview of Windows Terminal on the remote machine."""
        return self.status_reporter.get_windows_terminal_overview()

    def print_windows_terminal_overview(self) -> None:
        """Print overview of Windows Terminal on the remote machine."""
        self.status_reporter.print_windows_terminal_overview()

    def generate_status_summary(self) -> Dict[str, Any]:
        """Generate a concise status summary for monitoring."""
        return self.status_reporter.generate_status_summary(self.tab_config)

    def check_tab_specific_status(self, tab_name: str) -> Dict[str, Any]:
        """Get detailed status for a specific tab."""
        return self.status_reporter.check_tab_specific_status(tab_name, self.tab_config)


if __name__ == "__main__":
    # Example usage
    sample_tabs = {
        "🤖Bot1": ("~/code/bytesense/bithence", "python bot1.py --create_new_bot True"),
        "🤖Bot2": ("~/code/bytesense/bithence", "python bot2.py --create_new_bot True"),
        "📊Monitor": ("~", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"),
        "📝Logs": ("C:/logs", "Get-Content app.log -Wait")
    }

    # Replace 'myserver' with an actual SSH config alias for a Windows machine
    remote_name = "myserver"  # This should be in ~/.ssh/config
    session_name = "test_remote_session"

    try:
        # Create layout using the remote generator
        generator = WTRemoteLayoutGenerator(remote_name=remote_name, session_name_prefix=session_name)
        script_path = generator.create_wt_layout(sample_tabs)
        print(f"✅ Remote layout created successfully: {script_path}")

        # Check if Windows Terminal is available on remote
        wt_available = generator.check_wt_available()
        print(f"🖥️  Windows Terminal available on {remote_name}: {'✅' if wt_available else '❌'}")

        # Get remote Windows info
        windows_info = generator.get_remote_windows_info()
        if windows_info.get("wt_available"):
            print(f"📦 Remote system info: {windows_info.get('windows_info', 'Unknown')}")

        # Demonstrate serialization
        print("\n💾 Demonstrating serialization...")
        saved_path = generator.to_json()
        print(f"✅ Session saved to: {saved_path}")

        # List all saved sessions
        saved_sessions = WTRemoteLayoutGenerator.list_saved_sessions()
        print(f"📋 Available saved sessions: {saved_sessions}")

        # Demonstrate loading (using the full path)
        loaded_generator = WTRemoteLayoutGenerator.from_json(saved_path)
        print(f"✅ Session loaded successfully: {loaded_generator.session_name}")
        print(f"📊 Loaded tabs: {list(loaded_generator.tab_config.keys())}")

        # Show command preview
        preview = generator.get_layout_preview(sample_tabs)
        print(f"\n📋 Command Preview:\n{preview}")

        # Demonstrate status checking
        print(f"\n🔍 Checking command status on remote '{remote_name}':")
        generator.print_status_report()

        # Show Windows Terminal overview
        print(f"\n🖥️  Windows Terminal Overview:")
        generator.print_windows_terminal_overview()

        # Start the session (uncomment to actually start)
        # start_result = generator.start_wt_session()
        # print(f"Session start result: {start_result}")

        # Attach to session (uncomment to attach)
        # generator.attach_to_session()

        print(f"\n▶️  To start this session, run:")
        print(f"   generator.start_wt_session()")
        print(f"\n📎 To attach to this session, run:")
        print(f"   generator.attach_to_session()")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()