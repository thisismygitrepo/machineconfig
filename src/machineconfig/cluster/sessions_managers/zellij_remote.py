#!/usr/bin/env python3
from typing import Dict, Optional, List, Union, Any
from pathlib import Path
import logging
import json
import uuid
from datetime import datetime

from rich.console import Console

from machineconfig.cluster.sessions_managers.zellij_utils.remote_executor import RemoteExecutor
from machineconfig.cluster.sessions_managers.zellij_utils.layout_generator import LayoutGenerator
from machineconfig.cluster.sessions_managers.zellij_utils.process_monitor import ProcessMonitor
from machineconfig.cluster.sessions_managers.zellij_utils.session_manager import SessionManager
from machineconfig.cluster.sessions_managers.zellij_utils.status_reporter import StatusReporter
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "zellij_layouts", "layout_manager")


class ZellijRemoteLayoutGenerator:
    def __init__(self, remote_name: str, session_name_prefix: str):
        self.remote_name = remote_name
        self.session_name = session_name_prefix + "_" + LayoutGenerator.generate_random_suffix(8)
        self.layout_config: Optional[LayoutConfig] = None
        self.layout_path: Optional[str] = None

        # Initialize modular components
        self.remote_executor = RemoteExecutor(remote_name)
        self.layout_generator = LayoutGenerator()
        self.process_monitor = ProcessMonitor(self.remote_executor)
        self.session_manager = SessionManager(self.remote_executor, self.session_name, TMP_LAYOUT_DIR)
        self.status_reporter = StatusReporter(self.process_monitor, self.session_manager)

    def create_zellij_layout(self, layout_config: LayoutConfig, output_dir: Optional[str]) -> str:
        # Enhanced Rich logging for remote layout creation
        tab_count = len(layout_config["layoutTabs"])
        layout_name = layout_config["layoutName"]
        console.print(f"[bold cyan]📋 Creating Zellij layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} tabs[/bright_green] [magenta]for remote[/magenta] [bold yellow]'{self.remote_name}'[/bold yellow]")

        # Display tab summary for remote
        for tab in layout_config["layoutTabs"]:
            console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue] [dim]on[/dim] [yellow]{self.remote_name}[/yellow]")

        self.layout_config = layout_config.copy()
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = TMP_LAYOUT_DIR
        self.layout_path = self.layout_generator.create_layout_file(layout_config, output_path, self.session_name)
        return self.layout_path

    # Static methods for backward compatibility
    @staticmethod
    def run_remote_command(remote_name: str, command: str, timeout: int):
        executor = RemoteExecutor(remote_name)
        return executor.run_command(command, timeout)

    def to_dict(self) -> Dict[str, Any]:
        return {"remote_name": self.remote_name, "session_name": self.session_name, "layout_config": self.layout_config, "layout_path": self.layout_path, "created_at": datetime.now().isoformat(), "class_name": self.__class__.__name__}

    def to_json(self, file_path: Optional[Union[str, Path]]) -> str:
        # Generate file path if not provided
        if file_path is None:
            random_id = str(uuid.uuid4())[:8]
            default_dir = Path.home() / "tmp_results" / "zellij_sessions" / "serialized"
            default_dir.mkdir(parents=True, exist_ok=True)
            file_path_obj = default_dir / f"zellij_session_{random_id}.json"
        else:
            file_path_obj = Path(file_path)

        # Ensure .json extension
        if not str(file_path_obj).endswith(".json"):
            file_path_obj = file_path_obj.with_suffix(".json")

        # Ensure parent directory exists
        file_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Serialize to JSON
        data = self.to_dict()

        text = json.dumps(data, indent=2, ensure_ascii=False)
        file_path_obj.write_text(text, encoding="utf-8")

        logger.info(f"✅ Serialized ZellijRemoteLayoutGenerator to: {file_path_obj}")
        return str(file_path_obj)

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "ZellijRemoteLayoutGenerator":
        file_path = Path(file_path)

        # Ensure .json extension
        if not str(file_path).endswith(".json"):
            file_path = file_path.with_suffix(".json")

        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        # Load JSON data
        text = Path(file_path).read_text(encoding="utf-8")
        data = json.loads(text)

        # Validate that it's the correct class
        if data.get("class_name") != cls.__name__:
            logger.warning(f"Class name mismatch: expected {cls.__name__}, got {data.get('class_name')}")

        # Create new instance
        # Extract session name prefix by removing the suffix
        session_name = data["session_name"]
        if "_" in session_name:
            session_name_prefix = "_".join(session_name.split("_")[:-1])
        else:
            session_name_prefix = session_name

        instance = cls(remote_name=data["remote_name"], session_name_prefix=session_name_prefix)

        # Restore state
        instance.session_name = data["session_name"]
        instance.layout_config = data["layout_config"]
        instance.layout_path = data["layout_path"]

        logger.info(f"✅ Loaded ZellijRemoteLayoutGenerator from: {file_path}")
        return instance

    @staticmethod
    def list_saved_sessions(directory_path: Optional[Union[str, Path]]) -> List[str]:
        if directory_path is None:
            directory_path = Path.home() / "tmp_results" / "zellij_sessions" / "serialized"
        else:
            directory_path = Path(directory_path)

        if not directory_path.exists():
            return []

        json_files = [f.name for f in directory_path.glob("*.json")]
        return sorted(json_files)


if __name__ == "__main__":
    # Example usage with new schema
    sample_layout: LayoutConfig = {
        "layoutName": "RemoteBots",
        "layoutTabs": [
            {"tabName": "🤖Bot1", "startDir": "~/code/bytesense/bithence", "command": "~/scripts/fire -mO go1.py bot1 --kw create_new_bot True"},
            {"tabName": "🤖Bot2", "startDir": "~/code/bytesense/bithence", "command": "~/scripts/fire -mO go2.py bot2 --kw create_new_bot True"},
            {"tabName": "📊Monitor", "startDir": "~", "command": "htop"},
            {"tabName": "📝Logs", "startDir": "/var/log", "command": "tail -f /var/log/app.log"},
        ],
    }

    # Replace 'myserver' with an actual SSH config alias
    remote_name = "myserver"  # This should be in ~/.ssh/config
    session_name = "test_remote_session"

    try:
        # Create layout using the remote generator
        generator = ZellijRemoteLayoutGenerator(remote_name=remote_name, session_name_prefix=session_name)
        layout_path = generator.create_zellij_layout(sample_layout, None)
        print(f"✅ Remote layout created successfully: {layout_path}")

        # Demonstrate serialization
        print("\n💾 Demonstrating serialization...")
        saved_path = generator.to_json(None)
        print(f"✅ Session saved to: {saved_path}")

        # List all saved sessions
        saved_sessions = ZellijRemoteLayoutGenerator.list_saved_sessions(None)
        print(f"📋 Available saved sessions: {saved_sessions}")

        # Demonstrate loading (using the full path)
        loaded_generator = ZellijRemoteLayoutGenerator.from_json(saved_path)
        print(f"✅ Session loaded successfully: {loaded_generator.session_name}")
        if loaded_generator.layout_config:
            tab_names = [tab["tabName"] for tab in loaded_generator.layout_config["layoutTabs"]]
            print(f"📊 Loaded tabs: {tab_names}")

        # Demonstrate status checking
        print(f"\n🔍 Checking command status on remote '{remote_name}':")
        if not generator.layout_config:
            console.print("[bold red]❌ No layout config available[/bold red]")
        else:
            generator.status_reporter.print_status_report(generator.layout_config)

        # Start the session (uncomment to actually start)
        # start_result = generator.start_zellij_session()
        # print(f"Session start result: {start_result}")

        # Attach to session (uncomment to attach)
        # generator.attach_to_session()

    except Exception as e:
        print(f"❌ Error: {e}")
