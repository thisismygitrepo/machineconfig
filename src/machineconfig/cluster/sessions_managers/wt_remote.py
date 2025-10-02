#!/usr/bin/env python3
from typing import Optional, Any
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
from machineconfig.utils.schemas.layouts.layout_types import TabConfig, LayoutConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TMP_LAYOUT_DIR = Path.home() / "tmp_results" / "wt_layouts"


class WTRemoteLayoutGenerator:
    def __init__(self, layout_config: LayoutConfig, remote_name: str, session_name: str):
        self.remote_name: str = remote_name
        self.session_name: str = session_name
        self.layout_config: LayoutConfig = layout_config.copy()
        self.script_path: Optional[str] = None

        # Initialize modular components
        self.remote_executor = WTRemoteExecutor(remote_name)
        self.layout_generator = WTLayoutGenerator()
        self.process_monitor = WTProcessMonitor(self.remote_executor)
        self.session_manager = WTSessionManager(self.remote_executor, self.session_name, TMP_LAYOUT_DIR)
        self.status_reporter = WTStatusReporter(self.process_monitor, self.session_manager)

    def create_layout_file(self) -> bool:
        """Create Windows Terminal layout file and return success status."""
        tab_count = len(self.layout_config["layoutTabs"])
        logger.info(f"Creating Windows Terminal layout with {tab_count} tabs for remote '{self.remote_name}'")
        
        # Extract tabs from layout_config
        tabs: list[TabConfig] = self.layout_config["layoutTabs"]
        script_content = self.layout_generator.create_wt_script(tabs, self.session_name, window_name=None)
        
        # Write to file
        tmp_layout_dir = Path.home() / "tmp_results" / "wt_layouts" / "remote"
        tmp_layout_dir.mkdir(parents=True, exist_ok=True)
        random_suffix = WTLayoutGenerator.generate_random_suffix(8)
        script_file = tmp_layout_dir / f"wt_layout_{self.session_name}_{random_suffix}.ps1"
        script_file.write_text(script_content, encoding="utf-8")
        self.script_path = str(script_file.absolute())
        
        logger.info(f"✅ Remote layout created: {self.script_path}")
        return True

    # Legacy methods for backward compatibility

    def to_dict(self) -> dict[str, Any]:
        return {"remote_name": self.remote_name, "session_name": self.session_name, "layout_config": self.layout_config, "script_path": self.script_path, "created_at": datetime.now().isoformat(), "class_name": self.__class__.__name__}

    def to_json(self, file_path: Optional[str]) -> str:
        # Generate file path if not provided
        if file_path is None:
            random_id = str(uuid.uuid4())[:8]
            default_dir = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
            default_dir.mkdir(parents=True, exist_ok=True)
            path_obj = default_dir / f"wt_session_{random_id}.json"
        else:
            path_obj = Path(file_path)

        # Ensure .json extension
        if not str(path_obj).endswith(".json"):
            path_obj = path_obj.with_suffix(".json")

        # Ensure parent directory exists
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to JSON
        data = self.to_dict()

        text = json.dumps(data, indent=2, ensure_ascii=False)
        path_obj.write_text(text, encoding="utf-8")

        logger.info(f"✅ Serialized WTRemoteLayoutGenerator to: {path_obj}")
        return str(path_obj)

    @classmethod
    def from_json(cls, file_path: str) -> "WTRemoteLayoutGenerator":
        path_obj = Path(file_path)

        # Ensure .json extension
        if not str(path_obj).endswith(".json"):
            path_obj = path_obj.with_suffix(".json")

        if not path_obj.exists():
            raise FileNotFoundError(f"JSON file not found: {path_obj}")

        # Load JSON data
        text = path_obj.read_text(encoding="utf-8")
        data = json.loads(text)

        # Validate that it's the correct class
        if data.get("class_name") != cls.__name__:
            logger.warning(f"Class name mismatch: expected {cls.__name__}, got {data.get('class_name')}")

        # Create new instance
        instance = cls(
            layout_config=data["layout_config"],
            remote_name=data["remote_name"],
            session_name=data["session_name"]
        )
        instance.script_path = data["script_path"]

        logger.info(f"✅ Loaded WTRemoteLayoutGenerator from: {file_path}")
        return instance

    @staticmethod
    def list_saved_sessions(directory_path: Optional[str]) -> list[str]:
        if directory_path is None:
            dir_path = Path.home() / "tmp_results" / "wt_sessions" / "serialized"
        else:
            dir_path = Path(directory_path)

        if not dir_path.exists():
            return []

        json_files = [f.name for f in dir_path.glob("*.json")]
        return sorted(json_files)


if __name__ == "__main__":
    # Example usage
    sample_tabs: list[TabConfig] = [
        {"tabName": "🤖Bot1", "startDir": "~/code/bytesense/bithence", "command": "python bot1.py --create_new_bot True"},
        {"tabName": "🤖Bot2", "startDir": "~/code/bytesense/bithence", "command": "python bot2.py --create_new_bot True"},
        {"tabName": "📊Monitor", "startDir": "~", "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"},
        {"tabName": "📝Logs", "startDir": "C:/logs", "command": "Get-Content app.log -Wait"},
    ]

    # Replace 'myserver' with an actual SSH config alias for a Windows machine
    remote_name = "myserver"  # This should be in ~/.ssh/config
    session_name = "test_remote_session"

    try:
        # Create layout config from tabs
        sample_layout: LayoutConfig = {
            "layoutName": "RemoteBots",
            "layoutTabs": sample_tabs
        }
        
        # Create layout using the remote generator
        generator = WTRemoteLayoutGenerator(
            layout_config=sample_layout,
            remote_name=remote_name,
            session_name=session_name
        )
        generator.create_layout_file()
        
        print(f"✅ Remote layout created successfully: {generator.script_path}")

        # Check if Windows Terminal is available on remote
        wt_available = generator.remote_executor.check_wt_available()
        print(f"🖥️  Windows Terminal available on {remote_name}: {'✅' if wt_available else '❌'}")

        # Get remote Windows info
        windows_info = generator.remote_executor.get_remote_windows_info()
        if windows_info.get("wt_available"):
            print(f"📦 Remote system info: {windows_info.get('windows_info', 'Unknown')}")

        # Demonstrate serialization
        print("\n💾 Demonstrating serialization...")
        saved_path = generator.to_json(None)
        print(f"✅ Session saved to: {saved_path}")

        # List all saved sessions
        saved_sessions = WTRemoteLayoutGenerator.list_saved_sessions(None)
        print(f"📋 Available saved sessions: {saved_sessions}")

        # Demonstrate loading (using the full path)
        loaded_generator = WTRemoteLayoutGenerator.from_json(saved_path)
        print(f"✅ Session loaded successfully: {loaded_generator.session_name}")
        print(f"📊 Loaded tabs: {[tab['tabName'] for tab in loaded_generator.layout_config['layoutTabs']]}")

        # Show command preview
        preview = generator.layout_generator.generate_wt_command(sample_tabs)
        print(f"\n📋 Command Preview:\n{preview}")

        # Demonstrate status checking
        print(f"\n🔍 Checking command status on remote '{remote_name}':")
        generator.status_reporter.print_status_report(sample_tabs)

        # Show Windows Terminal overview
        print("\n🖥️  Windows Terminal Overview:")
        generator.status_reporter.print_windows_terminal_overview()

        # Start the session (uncomment to actually start)
        # start_result = generator.session_manager.start_wt_session(generator.script_path)
        # print(f"Session start result: {start_result}")

        # Attach to session (uncomment to attach)
        # generator.session_manager.attach_to_session()

        print("\n▶️  To start this session, run:")
        print("   generator.session_manager.start_wt_session(generator.script_path)")
        print("\n📎 To attach to this session, run:")
        print("   generator.session_manager.attach_to_session()")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
