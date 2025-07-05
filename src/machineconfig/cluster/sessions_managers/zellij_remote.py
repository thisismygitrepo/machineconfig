#!/usr/bin/env python3
"""
Main Zellij remote layout generator - orchestrates all remote session management.
"""
from typing import Dict, Tuple, Optional
from pathlib import Path
import logging

from machineconfig.cluster.sessions_managers.zellij_utils.remote_executor import RemoteExecutor
from machineconfig.cluster.sessions_managers.zellij_utils.layout_generator import LayoutGenerator
from machineconfig.cluster.sessions_managers.zellij_utils.process_monitor import ProcessMonitor
from machineconfig.cluster.sessions_managers.zellij_utils.session_manager import SessionManager
from machineconfig.cluster.sessions_managers.zellij_utils.status_reporter import StatusReporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "zellij_layouts", "layout_manager")


class ZellijRemoteLayoutGenerator:
    """Main orchestrator for Zellij remote layout generation and session management."""
    
    def __init__(self, remote_name: str, session_name_prefix: str):
        self.remote_name = remote_name
        self.session_name = session_name_prefix + LayoutGenerator.generate_random_suffix()
        self.tab_config: Dict[str, Tuple[str, str]] = {}
        self.layout_path: Optional[str] = None
        
        # Initialize modular components
        self.remote_executor = RemoteExecutor(remote_name)
        self.layout_generator = LayoutGenerator()
        self.process_monitor = ProcessMonitor(self.remote_executor)
        self.session_manager = SessionManager(self.remote_executor, self.session_name, TMP_LAYOUT_DIR)
        self.status_reporter = StatusReporter(self.process_monitor, self.session_manager)
    
    def copy_layout_to_remote(self, local_layout_file: Path, random_suffix: str) -> str:
        """Copy the layout file to the remote machine and return the remote path."""
        return self.session_manager.copy_layout_to_remote(local_layout_file, random_suffix)

    def create_zellij_layout(self, tab_config: Dict[str, Tuple[str, str]], output_dir: Optional[str] = None) -> str:
        """Create a Zellij layout file with the given tab configuration."""
        logger.info(f"Creating Zellij layout with {len(tab_config)} tabs for remote '{self.remote_name}'")
        
        # Store tab configuration
        self.tab_config = tab_config.copy()
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = TMP_LAYOUT_DIR
        
        # Create layout file using the layout generator
        self.layout_path = self.layout_generator.create_layout_file(tab_config, output_path, self.session_name)
        
        return self.layout_path
    
    def get_layout_preview(self, tab_config: Dict[str, Tuple[str, str]]) -> str:
        """Get a preview of the layout content without creating a file."""
        return self.layout_generator.generate_layout_content(tab_config)
    
    def check_command_status(self, tab_name: str, use_verification: bool = True) -> Dict[str, any]:
        """Check command status with optional process verification."""
        return self.process_monitor.check_command_status(tab_name, self.tab_config, use_verification)

    def check_all_commands_status(self) -> Dict[str, Dict[str, any]]:
        """Check status of all commands in the configuration."""
        return self.process_monitor.check_all_commands_status(self.tab_config)

    def check_zellij_session_status(self) -> Dict[str, any]:
        """Check if the Zellij session exists and is running."""
        return self.session_manager.check_zellij_session_status()

    def get_comprehensive_status(self) -> Dict[str, any]:
        """Get comprehensive status including session and all commands."""
        return self.status_reporter.get_comprehensive_status(self.tab_config)

    def print_status_report(self) -> None:
        """Print a formatted status report to console."""
        self.status_reporter.print_status_report(self.tab_config)

    def start_zellij_session(self, layout_file_path: Optional[str] = None) -> Dict[str, any]:
        """Start a Zellij session on the remote machine with the generated layout."""
        return self.session_manager.start_zellij_session(layout_file_path or self.layout_path)

    def attach_to_session(self) -> None:
        """Attach to the Zellij session on the remote machine via SSH."""
        self.session_manager.attach_to_session()

    # Legacy methods for backward compatibility
    def force_fresh_process_check(self, tab_name: str) -> Dict[str, any]:
        """Force a fresh process check with additional validation."""
        return self.process_monitor.force_fresh_process_check(tab_name, self.tab_config)

    def verify_process_alive(self, pid: int) -> bool:
        """Verify if a process with given PID is actually alive."""
        return self.process_monitor.verify_process_alive(pid)

    def get_verified_process_status(self, tab_name: str) -> Dict[str, any]:
        """Get process status with additional verification."""
        return self.process_monitor.get_verified_process_status(tab_name, self.tab_config)

    # Static methods for backward compatibility
    @staticmethod
    def run_remote_command(remote_name: str, command: str, timeout: int = 30):
        """Execute a command on the remote machine via SSH (legacy method)."""
        executor = RemoteExecutor(remote_name)
        return executor.run_command(command, timeout)

if __name__ == "__main__":
    # Example usage
    sample_tabs = {
        "🤖Bot1": ("~/code/bytesense/bithence", "~/scripts/fire -mO go1.py bot1 --kw create_new_bot True"),
        "🤖Bot2": ("~/code/bytesense/bithence", "~/scripts/fire -mO go2.py bot2 --kw create_new_bot True"), 
        "📊Monitor": ("~", "htop"),
        "📝Logs": ("/var/log", "tail -f /var/log/app.log")
    }
    
    # Replace 'myserver' with an actual SSH config alias
    remote_name = "myserver"  # This should be in ~/.ssh/config
    session_name = "test_remote_session"
    
    try:
        # Create layout using the remote generator
        generator = ZellijRemoteLayoutGenerator(remote_name=remote_name, session_name_prefix=session_name)
        layout_path = generator.create_zellij_layout(sample_tabs)
        print(f"✅ Remote layout created successfully: {layout_path}")
        
        # Demonstrate status checking
        print(f"\n🔍 Checking command status on remote '{remote_name}':")
        generator.print_status_report()
        
        # Start the session (uncomment to actually start)
        # start_result = generator.start_zellij_session()
        # print(f"Session start result: {start_result}")
        
        # Attach to session (uncomment to attach)
        # generator.attach_to_session()
        
    except Exception as e:
        print(f"❌ Error: {e}")
