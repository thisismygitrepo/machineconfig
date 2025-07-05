#!/usr/bin/env python3
import shlex
import subprocess
import json
import random
import string
from typing import Dict, List, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "zellij_layouts", "layout_manager")


class ZellijRemoteLayoutGenerator:
    def __init__(self, remote_name: str, default_cwd: Optional[str] = None):
        self.remote_name = remote_name
        self.default_cwd = default_cwd or "~"
        self.session_name: Optional[str] = None
        self.tab_commands = {}  # Store tab commands for status checking
        self.random_suffix = self._generate_random_suffix()  # Generate unique suffix
        self.layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
    
    def _generate_random_suffix(self, length: int = 8) -> str:
        """Generate a random string suffix for unique layout file names."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _run_remote_command(self, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute a command on the remote machine via SSH."""
        ssh_cmd = ["ssh", self.remote_name, command]
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"SSH command timed out after {timeout}s: {command}")
            raise
        except Exception as e:
            logger.error(f"SSH command failed: {e}")
            raise
    
    def _parse_command(self, command: str) -> tuple[str, List[str]]:
        try:
            parts = shlex.split(command)
            if not parts: 
                raise ValueError("Empty command provided")
            return parts[0], parts[1:] if len(parts) > 1 else []
        except ValueError as e:
            logger.error(f"Error parsing command '{command}': {e}")
            parts = command.split()
            return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []
    
    def _format_args_for_kdl(self, args: List[str]) -> str:
        if not args: 
            return ""
        formatted_args = []
        for arg in args:
            if ' ' in arg or '"' in arg or "'" in arg:
                escaped_arg = arg.replace('"', '\\"')
                formatted_args.append(f'"{escaped_arg}"')
            else:
                formatted_args.append(f'"{arg}"')
        return " ".join(formatted_args)
    
    def _create_tab_section(self, tab_name: str, cwd: str, command: str) -> str:
        cmd, args = self._parse_command(command)
        args_str = self._format_args_for_kdl(args)
        tab_cwd = cwd or self.default_cwd
        escaped_tab_name = tab_name.replace('"', '\\"')
        tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str: 
            tab_section += f'      args {args_str}\n'
        tab_section += '    }\n  }\n'
        return tab_section
    
    def _validate_tab_config(self, tab_config: Dict[str, tuple[str, str]]) -> None:
        if not tab_config: 
            raise ValueError("Tab configuration cannot be empty")
        for tab_name, (cwd, command) in tab_config.items():
            if not tab_name.strip(): 
                raise ValueError(f"Invalid tab name: {tab_name}")
            if not command.strip(): 
                raise ValueError(f"Invalid command for tab '{tab_name}': {command}")
            if not cwd.strip(): 
                raise ValueError(f"Invalid cwd for tab '{tab_name}': {cwd}")
    
    def create_zellij_layout(self, tab_config: Dict[str, tuple[str, str]], output_dir: Optional[str] = None, session_name: Optional[str] = None) -> str:
        self._validate_tab_config(tab_config)
        logger.info(f"Creating Zellij layout with {len(tab_config)} tabs for remote '{self.remote_name}'")
        
        # Store session name and tab commands for status checking
        self.session_name = session_name or "default"
        self.tab_commands = {tab_name: command for tab_name, (_, command) in tab_config.items()}
        
        layout_content = self.layout_template
        for tab_name, (cwd, command) in tab_config.items():
            layout_content += "\n" + self._create_tab_section(tab_name, cwd, command)
        layout_content += "\n}\n"
        
        try:
            # Create layout file locally first
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                layout_file = output_path / f"zellij_layout_{self.random_suffix}.kdl"
            else:
                # Use the predefined TMP_LAYOUT_DIR for temporary files
                TMP_LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
                layout_file = TMP_LAYOUT_DIR / f"zellij_layout_{self.session_name or 'default'}_{self.random_suffix}.kdl"
            
            # Write layout file locally
            with open(layout_file, 'w', encoding='utf-8') as f:
                f.write(layout_content)
            
            # Create remote directory and copy layout file
            remote_layout_dir = f"~/tmp_results/zellij_layouts/layout_manager"
            remote_layout_file = f"{remote_layout_dir}/zellij_layout_{self.session_name or 'default'}_{self.random_suffix}.kdl"
            
            # Create remote directory
            mkdir_result = self._run_remote_command(f"mkdir -p {remote_layout_dir}")
            if mkdir_result.returncode != 0:
                raise RuntimeError(f"Failed to create remote directory: {mkdir_result.stderr}")
            
            # Copy layout file to remote machine
            scp_cmd = ["scp", str(layout_file), f"{self.remote_name}:{remote_layout_file}"]
            scp_result = subprocess.run(scp_cmd, capture_output=True, text=True)
            if scp_result.returncode != 0:
                raise RuntimeError(f"Failed to copy layout file to remote: {scp_result.stderr}")
            
            logger.info(f"Zellij layout file created locally: {layout_file.absolute()}")
            logger.info(f"Zellij layout file copied to remote: {self.remote_name}:{remote_layout_file}")
            
            return str(layout_file.absolute())
            
        except OSError as e:
            logger.error(f"Failed to create layout file: {e}")
            raise
    
    def get_layout_preview(self, tab_config: Dict[str, tuple[str, str]]) -> str:
        self._validate_tab_config(tab_config)
        layout_content = self.layout_template
        for tab_name, (cwd, command) in tab_config.items():
            layout_content += "\n" + self._create_tab_section(tab_name, cwd, command)
        return layout_content + "\n}\n"
    
    def check_command_status(self, tab_name: str) -> Dict[str, any]:
        if tab_name not in self.tab_commands:
            return {
                "status": "unknown",
                "error": f"Tab '{tab_name}' not found in tracked commands",
                "running": False,
                "pid": None,
                "command": None,
                "remote": self.remote_name
            }
        
        command = self.tab_commands[tab_name]
        cmd, args = self._parse_command(command)
        
        try:
            # Create a Python script to check processes on remote machine
            check_script = f"""
import psutil
import json

def check_process():
    matching_processes = []
    cmd = '{cmd}'
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                if (proc.info['name'] == cmd or 
                    cmd in proc.info['cmdline'][0] or
                    any(cmd in str(arg) for arg in proc.info['cmdline'])):
                    matching_processes.append({{
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": proc.info['cmdline'],
                        "status": proc.info['status']
                    }})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return matching_processes

if __name__ == "__main__":
    processes = check_process()
    print(json.dumps(processes))
"""
            
            # Execute the check script on remote machine
            remote_cmd = f"python3 -c {shlex.quote(check_script)}"
            result = self._run_remote_command(remote_cmd, timeout=15)
            
            if result.returncode == 0:
                try:
                    matching_processes = json.loads(result.stdout.strip())
                    
                    if matching_processes:
                        return {
                            "status": "running",
                            "running": True,
                            "processes": matching_processes,
                            "command": command,
                            "tab_name": tab_name,
                            "remote": self.remote_name
                        }
                    else:
                        return {
                            "status": "not_running",
                            "running": False,
                            "processes": [],
                            "command": command,
                            "tab_name": tab_name,
                            "remote": self.remote_name
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse remote process check output: {e}")
                    return {
                        "status": "error",
                        "error": f"Failed to parse remote output: {e}",
                        "running": False,
                        "command": command,
                        "tab_name": tab_name,
                        "remote": self.remote_name
                    }
            else:
                return {
                    "status": "error",
                    "error": f"Remote command failed: {result.stderr}",
                    "running": False,
                    "command": command,
                    "tab_name": tab_name,
                    "remote": self.remote_name
                }
                
        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}' on remote '{self.remote_name}': {e}")
            return {
                "status": "error",
                "error": str(e),
                "running": False,
                "command": command,
                "tab_name": tab_name,
                "remote": self.remote_name
            }

    def check_all_commands_status(self) -> Dict[str, Dict[str, any]]:
        if not self.tab_commands:
            logger.warning("No tab commands tracked. Make sure to create a layout first.")
            return {}
        
        status_report = {}
        for tab_name in self.tab_commands:
            status_report[tab_name] = self.check_command_status(tab_name)
        
        return status_report

    def check_zellij_session_status(self) -> Dict[str, any]:
        try:
            # Run zellij list-sessions command on remote machine
            result = self._run_remote_command('zellij list-sessions', timeout=10)
            
            if result.returncode == 0:
                sessions = result.stdout.strip().split('\n') if result.stdout.strip() else []
                session_running = any(self.session_name in session for session in sessions)
                
                return {
                    "zellij_running": True,
                    "session_exists": session_running,
                    "session_name": self.session_name,
                    "all_sessions": sessions,
                    "remote": self.remote_name
                }
            else:
                return {
                    "zellij_running": False,
                    "error": result.stderr,
                    "session_name": self.session_name,
                    "remote": self.remote_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                "zellij_running": False,
                "error": "Timeout while checking Zellij sessions on remote",
                "session_name": self.session_name,
                "remote": self.remote_name
            }
        except Exception as e:
            return {
                "zellij_running": False,
                "error": str(e),
                "session_name": self.session_name,
                "remote": self.remote_name
            }

    def get_comprehensive_status(self) -> Dict[str, any]:
        zellij_status = self.check_zellij_session_status()
        commands_status = self.check_all_commands_status()
        
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
                "remote": self.remote_name
            }
        }

    def print_status_report(self) -> None:
        status = self.get_comprehensive_status()
        
        print("=" * 60)
        print(f"🔍 ZELLIJ REMOTE LAYOUT STATUS REPORT ({self.remote_name})")
        print("=" * 60)
        
        # Zellij session status
        zellij = status["zellij_session"]
        if zellij.get("zellij_running", False):
            if zellij.get("session_exists", False):
                print(f"✅ Zellij session '{self.session_name}' is running on {self.remote_name}")
            else:
                print(f"⚠️  Zellij is running on {self.remote_name} but session '{self.session_name}' not found")
        else:
            print(f"❌ Zellij session issue on {self.remote_name}: {zellij.get('error', 'Unknown error')}")
        
        print()
        
        # Commands status
        print("📋 COMMAND STATUS:")
        print("-" * 40)
        
        for tab_name, cmd_status in status["commands"].items():
            if cmd_status.get("running", False):
                print(f"✅ {tab_name}: Running on {self.remote_name}")
                if cmd_status.get("processes"):
                    for proc in cmd_status["processes"][:2]:  # Show first 2 processes
                        print(f"   └─ PID {proc['pid']}: {proc['name']} ({proc['status']})")
            else:
                print(f"❌ {tab_name}: Not running on {self.remote_name}")
            print(f"   Command: {cmd_status.get('command', 'Unknown')}")
            print()
        
        # Summary
        summary = status["summary"]
        print("📊 SUMMARY:")
        print(f"   Remote machine: {self.remote_name}")
        print(f"   Total commands: {summary['total_commands']}")
        print(f"   Running: {summary['running_commands']}")
        print(f"   Stopped: {summary['stopped_commands']}")
        print(f"   Session healthy: {'✅' if summary['session_healthy'] else '❌'}")
        print("=" * 60)

    def start_zellij_session(self, layout_file_path: Optional[str] = None) -> Dict[str, any]:
        """Start a Zellij session on the remote machine with the generated layout."""
        try:
            if layout_file_path:
                remote_layout_file = f"~/tmp_results/zellij_layouts/layout_manager/zellij_layout_{self.session_name or 'default'}_{self.random_suffix}.kdl"
            else:
                remote_layout_file = f"~/tmp_results/zellij_layouts/layout_manager/zellij_layout_{self.session_name or 'default'}_{self.random_suffix}.kdl"
            
            # Start Zellij session with layout
            start_cmd = f"zellij --session {self.session_name} --layout {remote_layout_file}"
            result = self._run_remote_command(start_cmd, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Zellij session '{self.session_name}' started on {self.remote_name}")
                return {
                    "success": True,
                    "session_name": self.session_name,
                    "remote": self.remote_name,
                    "message": f"Session started successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "session_name": self.session_name,
                    "remote": self.remote_name
                }
                
        except Exception as e:
            logger.error(f"Failed to start Zellij session on {self.remote_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_name": self.session_name,
                "remote": self.remote_name
            }

    def attach_to_session(self) -> None:
        """Attach to the Zellij session on the remote machine via SSH."""
        try:
            attach_cmd = ["ssh", "-t", self.remote_name, f"zellij attach {self.session_name}"]
            logger.info(f"Attaching to Zellij session '{self.session_name}' on {self.remote_name}")
            # This will transfer control to the SSH session
            subprocess.run(attach_cmd)
        except Exception as e:
            logger.error(f"Failed to attach to session: {e}")
            raise


# Legacy functions for backward compatibility
def copy_layout_to_remote(remote_machine: str, local_layout_path: str, remote_layout_path: str | None = None) -> str:
    """Legacy function for copying layout files to remote machines."""
    local_path = Path(local_layout_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local layout file not found: {local_layout_path}")
    
    # Use same path on remote if not specified, but resolve relative to remote home
    if remote_layout_path is None:
        local_home = Path.home()
        local_abs_path = local_path.resolve()
        # Check if the local path is within the home directory
        try:
            relative_to_home = local_abs_path.relative_to(local_home)
            # Use the relative path from home, which will resolve to the remote user's home
            remote_layout_path = f"~/{relative_to_home}"
        except ValueError:
            # If path is not relative to home, just use the filename in remote home
            remote_layout_path = f"~/{local_path.name}"    
    
    # Copy the layout file to remote machine
    scp_command = [
        "scp", 
        str(local_path), 
        f"{remote_machine}:{remote_layout_path}"
    ]
    print(f"📁 Copying layout file to {remote_machine}:{remote_layout_path}")
    result = subprocess.run(scp_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to copy layout file: {result.stderr}")    
    return remote_layout_path


def execute_zellij_layout(remote_machine: str, remote_layout_path: str, session_name: str = "JobManager"):
    """Legacy function for executing zellij layouts on remote machines."""
    # Execute zellij with the layout on remote machine
    ssh_command = [
        "ssh", remote_machine, "-n",
        f". ~/.profile; . ~/.bashrc; zellij --layout {remote_layout_path} a -b {session_name}"
    ]
    
    print(f"🚀 Executing zellij layout on {remote_machine}")
    result = subprocess.run(ssh_command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️  Warning: SSH command returned non-zero exit code: {result.stderr}")
    else:
        print(f"✅ Successfully launched zellij layout on {remote_machine}")
    
    return result


def create_remote_zellij_layout(remote_name: str, tab_config: Dict[str, tuple[str, str]], output_dir: Optional[str] = None, default_cwd: Optional[str] = None, session_name: Optional[str] = None) -> str:
    """Convenience function to create a remote Zellij layout."""
    generator = ZellijRemoteLayoutGenerator(remote_name=remote_name, default_cwd=default_cwd)
    return generator.create_zellij_layout(tab_config, output_dir, session_name)


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
    
    try:
        # Create layout using the remote generator
        generator = ZellijRemoteLayoutGenerator(remote_name=remote_name)
        layout_path = generator.create_zellij_layout(sample_tabs, session_name="test_remote_session")
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


def send_and_execute_zellij_layout(remote_machine: str, local_layout_path: str, remote_layout_path: str | None = None, session_name: str = "JobManager"):
    remote_path = copy_layout_to_remote(remote_machine, local_layout_path, remote_layout_path)
    return execute_zellij_layout(remote_machine, remote_path, session_name)
