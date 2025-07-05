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
    def __init__(self, remote_name: str, session_name_prefix: str):
        self.remote_name = remote_name
        self.session_name = session_name_prefix + ZellijRemoteLayoutGenerator._generate_random_suffix()
        self.tab_config: Dict[str, tuple[str, str]] = {}  # Store entire tab configuration (name -> (cwd, command))
        self.layout_path: Optional[str] = None  # Store the full layout file path
        self.layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
    
    @staticmethod
    def _generate_random_suffix(length: int = 8) -> str:
        """Generate a random string suffix for unique layout file names."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def _run_remote_command(remote_name: str, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute a command on the remote machine via SSH."""
        ssh_cmd = ["ssh", remote_name, command]
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
    
    @staticmethod
    def _parse_command(command: str) -> tuple[str, List[str]]:
        try:
            parts = shlex.split(command)
            if not parts: 
                raise ValueError("Empty command provided")
            return parts[0], parts[1:] if len(parts) > 1 else []
        except ValueError as e:
            logger.error(f"Error parsing command '{command}': {e}")
            parts = command.split()
            return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []
    
    @staticmethod
    def _format_args_for_kdl(args: List[str]) -> str:
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
    
    @staticmethod
    def _create_tab_section(tab_name: str, cwd: str, command: str) -> str:
        cmd, args = ZellijRemoteLayoutGenerator._parse_command(command)
        args_str = ZellijRemoteLayoutGenerator._format_args_for_kdl(args)
        tab_cwd = cwd or "~"
        escaped_tab_name = tab_name.replace('"', '\\"')
        tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str: 
            tab_section += f'      args {args_str}\n'
        tab_section += '    }\n  }\n'
        return tab_section
    
    @staticmethod
    def _validate_tab_config(tab_config: Dict[str, tuple[str, str]]) -> None:
        if not tab_config: 
            raise ValueError("Tab configuration cannot be empty")
        for tab_name, (cwd, command) in tab_config.items():
            if not tab_name.strip(): 
                raise ValueError(f"Invalid tab name: {tab_name}")
            if not command.strip(): 
                raise ValueError(f"Invalid command for tab '{tab_name}': {command}")
            if not cwd.strip(): 
                raise ValueError(f"Invalid cwd for tab '{tab_name}': {cwd}")
    
    def copy_layout_to_remote(self, local_layout_file: Path, random_suffix: str) -> str:
        """Copy the layout file to the remote machine and return the remote path."""
        # Create remote directory and copy layout file
        remote_layout_dir = f"~/{TMP_LAYOUT_DIR.relative_to(Path.home())}"
        remote_layout_file = f"{remote_layout_dir}/zellij_layout_{self.session_name}_{random_suffix}.kdl"
        
        # Create remote directory
        mkdir_result = self._run_remote_command(self.remote_name, f"mkdir -p {remote_layout_dir}")
        if mkdir_result.returncode != 0:
            raise RuntimeError(f"Failed to create remote directory: {mkdir_result.stderr}")
        
        # Copy layout file to remote machine
        scp_cmd = ["scp", str(local_layout_file), f"{self.remote_name}:{remote_layout_file}"]
        scp_result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if scp_result.returncode != 0:
            raise RuntimeError(f"Failed to copy layout file to remote: {scp_result.stderr}")
        
        logger.info(f"Zellij layout file copied to remote: {self.remote_name}:{remote_layout_file}")
        return remote_layout_file

    def create_zellij_layout(self, tab_config: Dict[str, tuple[str, str]], output_dir: Optional[str] = None) -> str:
        self._validate_tab_config(tab_config)
        logger.info(f"Creating Zellij layout with {len(tab_config)} tabs for remote '{self.remote_name}'")
        
        # Store tab configuration
        self.tab_config = tab_config.copy()  # Store the entire tab configuration
        
        # Generate unique suffix for this layout
        random_suffix = self._generate_random_suffix()
        
        layout_content = self.layout_template
        for tab_name, (cwd, command) in tab_config.items():
            layout_content += "\n" + self._create_tab_section(tab_name, cwd, command)
        layout_content += "\n}\n"
        
        try:
            # Create layout file locally first
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                layout_file = output_path / f"zellij_layout_{random_suffix}.kdl"
            else:
                # Use the predefined TMP_LAYOUT_DIR for temporary files
                TMP_LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
                layout_file = TMP_LAYOUT_DIR / f"zellij_layout_{self.session_name}_{random_suffix}.kdl"
            
            # Store the layout path as an attribute
            self.layout_path = str(layout_file.absolute())
            
            # Write layout file locally
            with open(layout_file, 'w', encoding='utf-8') as f:
                f.write(layout_content)
            
            logger.info(f"Zellij layout file created locally: {layout_file.absolute()}")
            
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
    
    def check_command_status(self, tab_name: str, use_verification: bool = True) -> Dict[str, any]:
        """Check command status with optional process verification."""
        if tab_name not in self.tab_config:
            return {
                "status": "unknown",
                "error": f"Tab '{tab_name}' not found in tracked configuration",
                "running": False,
                "pid": None,
                "command": None,
                "remote": self.remote_name
            }
        
        # Use the verified method by default for more accurate results
        if use_verification:
            return self.get_verified_process_status(tab_name)
        
        cwd, command = self.tab_config[tab_name]
        cmd, args = self._parse_command(command)
        
        try:
            # Create a Python script to check processes on remote machine
            # Use the full command for better matching, not just the first part
            check_script = f"""
import psutil
import json
import os

def check_process():
    matching_processes = []
    full_command = '{command}'
    cmd_parts = [part for part in full_command.split() if len(part) > 2]  # Only significant parts
    current_pid = os.getpid()
    
    # More specific command patterns to match
    primary_cmd = cmd_parts[0] if cmd_parts else ''
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            # Skip the current process (this script itself)
            if proc.info['pid'] == current_pid:
                continue
                
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline_str = ' '.join(proc.info['cmdline'])
                
                # Skip if this is clearly the psutil check script itself
                if 'check_process()' in cmdline_str or 'psutil.process_iter' in cmdline_str:
                    continue
                
                # More precise matching - require primary command to be present
                # and at least 2 other significant parts
                matches_primary = primary_cmd in cmdline_str
                matches_parts = sum(1 for part in cmd_parts[1:] if part in cmdline_str)
                
                # Only match if we have the primary command and at least 2 other parts
                # OR if the full command string is present (but not in a Python script)
                if (matches_primary and matches_parts >= 2) or \\
                   (full_command in cmdline_str and not any(python_indicator in cmdline_str.lower() 
                                                           for python_indicator in ['python -c', 'import psutil', 'def check_process'])):
                    matching_processes.append({{
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": proc.info['cmdline'],
                        "status": proc.info['status'],
                        "cmdline_str": cmdline_str,
                        "create_time": proc.info['create_time']
                    }})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return matching_processes

if __name__ == "__main__":
    processes = check_process()
    print(json.dumps(processes))
"""
            
            # Execute the check script on remote machine using the virtual environment Python
            remote_cmd = f"$HOME/venvs/ve/bin/python -c {shlex.quote(check_script)}"
            result = self._run_remote_command(self.remote_name, remote_cmd, timeout=15)
            
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
                    logger.error(f"Raw output was: {result.stdout}")
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
        if not self.tab_config:
            logger.warning("No tab configuration tracked. Make sure to create a layout first.")
            return {}
        
        status_report = {}
        for tab_name in self.tab_config:
            status_report[tab_name] = self.check_command_status(tab_name)
        return status_report

    def check_zellij_session_status(self) -> Dict[str, any]:
        try:
            # Run zellij list-sessions command on remote machine
            result = self._run_remote_command(self.remote_name, 'zellij list-sessions', timeout=10)
            
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
                # Extract filename from provided path
                layout_filename = Path(layout_file_path).name
                remote_layout_file = f"~/{TMP_LAYOUT_DIR.relative_to(Path.home())}/{layout_filename}"
            elif self.layout_path:
                # Use stored layout path
                layout_filename = Path(self.layout_path).name
                remote_layout_file = f"~/{TMP_LAYOUT_DIR.relative_to(Path.home())}/{layout_filename}"
            else:
                raise ValueError("No layout file path available. Create a layout first.")
            
            print(f"Starting Zellij session '{self.session_name}' on remote '{self.remote_name}' with layout: {remote_layout_file}")
            # Start Zellij session with layout
            start_cmd = f"zellij --layout {remote_layout_file} a -b {self.session_name}"
            print(f"Executing command: {start_cmd}")
            result = self._run_remote_command(self.remote_name, start_cmd, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Zellij session '{self.session_name}' started on {self.remote_name}")
                return {
                    "success": True,
                    "session_name": self.session_name,
                    "remote": self.remote_name,
                    "message": "Session started successfully"
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

    def debug_remote_process_check(self, tab_name: str) -> Dict[str, any]:
        """Debug method to manually check what's happening on the remote machine."""
        if tab_name not in self.tab_config:
            return {"error": f"Tab '{tab_name}' not found in configuration"}
        
        cwd, command = self.tab_config[tab_name]
        cmd, args = self._parse_command(command)
        
        debug_info = {
            "tab_name": tab_name,
            "command": command,
            "parsed_cmd": cmd,
            "parsed_args": args,
            "remote": self.remote_name,
            "checks": {}
        }
        
        # Check 1: What the psutil script actually returns
        try:
            # Escape the command properly for the debug script
            escaped_command = command.replace("'", "\\'").replace('"', '\\"')
            
            check_script = f'''
import psutil
import json
import os

def check_process():
    all_processes = []
    matching_processes = []
    full_command = '{escaped_command}'
    cmd_parts = [part for part in full_command.split() if len(part) > 2]
    current_pid = os.getpid()
    primary_cmd = cmd_parts[0] if cmd_parts else ''
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            # Skip current process
            if proc.info['pid'] == current_pid:
                continue
                
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline_str = ' '.join(proc.info['cmdline'])
                
                # Log all processes for debugging (excluding psutil scripts)
                if not any(indicator in cmdline_str for indicator in ['check_process()', 'psutil.process_iter']):
                    all_processes.append({{
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline_str": cmdline_str[:100] + "..." if len(cmdline_str) > 100 else cmdline_str
                    }})
                
                # Skip if this is clearly the psutil check script itself
                if 'check_process()' in cmdline_str or 'psutil.process_iter' in cmdline_str:
                    continue
                
                # More precise matching
                matches_primary = primary_cmd in cmdline_str and primary_cmd != 'python'
                matches_parts = sum(1 for part in cmd_parts[1:] if part in cmdline_str)
                
                # Debug info for matching logic
                match_info = {{
                    "primary_cmd": primary_cmd,
                    "matches_primary": matches_primary,
                    "matches_parts": matches_parts,
                    "cmd_parts": cmd_parts[1:],
                    "full_command_match": full_command in cmdline_str,
                    "is_python_script": any(python_indicator in cmdline_str.lower() 
                                          for python_indicator in ['python -c', 'import psutil', 'def check_process'])
                }}
                
                if (matches_primary and matches_parts >= 2) or \\
                   (full_command in cmdline_str and not match_info["is_python_script"]):
                    matching_processes.append({{
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": proc.info['cmdline'],
                        "status": proc.info['status'],
                        "cmdline_str": cmdline_str,
                        "create_time": proc.info['create_time'],
                        "match_info": match_info
                    }})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return {{
        "matching": matching_processes, 
        "all_processes": all_processes[:20],  # First 20 for debugging
        "search_info": {{
            "full_command": full_command,
            "cmd_parts": cmd_parts,
            "primary_cmd": primary_cmd
        }}
    }}

if __name__ == "__main__":
    result = check_process()
    print(json.dumps(result))
'''
            remote_cmd = f"$HOME/venvs/ve/bin/python -c {shlex.quote(check_script)}"
            result = self._run_remote_command(self.remote_name, remote_cmd, timeout=15)
            debug_info["checks"]["psutil_detailed"] = {
                "command": remote_cmd,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            debug_info["checks"]["psutil_detailed"] = {"error": str(e)}
        
        return debug_info

    def test_process_detection_methods(self, tab_name: str) -> Dict[str, any]:
        """Test different process detection methods side by side for comparison."""
        if tab_name not in self.tab_config:
            return {"error": f"Tab '{tab_name}' not found in configuration"}
        
        results = {
            "tab_name": tab_name,
            "command": self.tab_config[tab_name][1],
            "remote": self.remote_name,
            "methods": {}
        }
        
        # Test old method (if you want to compare)
        try:
            # This uses the updated check_command_status with use_verification=False
            old_result = self.check_command_status(tab_name, use_verification=False)
            results["methods"]["old_method"] = old_result
        except Exception as e:
            results["methods"]["old_method"] = {"error": str(e)}
        
        # Test new fresh check method
        try:
            fresh_result = self.force_fresh_process_check(tab_name)
            results["methods"]["fresh_check"] = fresh_result
        except Exception as e:
            results["methods"]["fresh_check"] = {"error": str(e)}
        
        # Test verified method (fresh + alive verification)
        try:
            verified_result = self.get_verified_process_status(tab_name)
            results["methods"]["verified_method"] = verified_result
        except Exception as e:
            results["methods"]["verified_method"] = {"error": str(e)}
        
        return results

    def print_test_results(self, tab_name: str) -> None:
        """Print a formatted comparison of different detection methods."""
        results = self.test_process_detection_methods(tab_name)
        
        print("=" * 80)
        print(f"🧪 PROCESS DETECTION METHODS COMPARISON")
        print("=" * 80)
        print(f"Tab: {results['tab_name']}")
        print(f"Command: {results['command']}")
        print(f"Remote: {results['remote']}")
        print()
        
        for method_name, method_result in results["methods"].items():
            print(f"--- {method_name.upper().replace('_', ' ')} ---")
            if "error" in method_result:
                print(f"❌ Error: {method_result['error']}")
            else:
                running = method_result.get("running", False)
                status_icon = "✅" if running else "❌"
                print(f"{status_icon} Status: {method_result.get('status', 'unknown')}")
                print(f"   Running: {running}")
                if method_result.get("processes"):
                    print(f"   Processes found: {len(method_result['processes'])}")
                    for i, proc in enumerate(method_result["processes"][:3]):  # Show first 3
                        verified = proc.get("verified_alive", "N/A")
                        print(f"     {i+1}. PID {proc['pid']}: {proc['name']} (verified: {verified})")
                else:
                    print("   Processes found: 0")
            print()
        
        print("=" * 80)

    def debug_remote_process_check_v2(self, tab_name: str) -> Dict[str, any]:
        """Debug method to check process detection methods."""
        if tab_name not in self.tab_config:
            return {"error": f"Tab '{tab_name}' not found in configuration"}
        
        cwd, command = self.tab_config[tab_name]
        cmd, args = self._parse_command(command)
        
        debug_info = {
            "tab_name": tab_name,
            "command": command,
            "parsed_cmd": cmd,
            "parsed_args": args,
            "remote": self.remote_name,
            "checks": {}
        }
        
        # Check using old method (for comparison)
        try:
            old_status = self.check_command_status(tab_name, use_verification=False)
            debug_info["checks"]["old_method"] = old_status
        except Exception as e:
            debug_info["checks"]["old_method"] = {"error": str(e)}
        
        # Check using fresh method
        try:
            fresh_status = self.force_fresh_process_check(tab_name)
            debug_info["checks"]["fresh_check"] = fresh_status
        except Exception as e:
            debug_info["checks"]["fresh_check"] = {"error": str(e)}
        
        # Check using verified method
        try:
            verified_status = self.get_verified_process_status(tab_name)
            debug_info["checks"]["verified_method"] = verified_status
        except Exception as e:
            debug_info["checks"]["verified_method"] = {"error": str(e)}
        
        return debug_info

    def print_debug_info_v2(self, tab_name: str) -> None:
        """Print formatted debug information for process detection methods."""
        debug_info = self.debug_remote_process_check_v2(tab_name)
        
        print("=" * 60)
        print(f"🐛 DEBUG INFO FOR TAB: {tab_name}")
        print("=" * 60)
        print(f"Remote: {debug_info['remote']}")
        print(f"Command: {debug_info['command']}")
        print(f"Parsed cmd: {debug_info['parsed_cmd']}")
        print(f"Parsed args: {debug_info['parsed_args']}")
        print()
        
        for check_name, check_result in debug_info["checks"].items():
            print(f"--- {check_name.upper()} ---")
            if "error" in check_result:
                print(f"❌ Error: {check_result['error']}")
            else:
                print(f"Return code: {check_result['returncode']}")
                if check_result['stdout']:
                    try:
                        # Try to parse JSON output for psutil_detailed
                        if check_name == "psutil_detailed" and check_result['returncode'] == 0:
                            data = json.loads(check_result['stdout'])
                            print(f"Matching processes: {len(data.get('matching', []))}")
                            for proc in data.get('matching', []):
                                print(f"  - PID {proc['pid']}: {proc['name']} -> {proc['cmdline_str']}")
                            print(f"Sample of all processes (first 10):")
                            for proc in data.get('all_processes', []):
                                print(f"  - PID {proc['pid']}: {proc['name']} -> {proc['cmdline_str']}")
                        else:
                            print(f"Stdout: {check_result['stdout']}")
                    except json.JSONDecodeError:
                        print(f"Stdout: {check_result['stdout']}")
                if check_result['stderr']:
                    print(f"Stderr: {check_result['stderr']}")
            print()
        print("=" * 60)
    
    def force_fresh_process_check(self, tab_name: str) -> Dict[str, any]:
        """Force a fresh process check with additional validation to avoid stale results."""
        if tab_name not in self.tab_config:
            return {
                "status": "unknown",
                "error": f"Tab '{tab_name}' not found in tracked configuration",
                "running": False,
                "command": None,
                "remote": self.remote_name
            }
        
        cwd, command = self.tab_config[tab_name]
        cmd, args = self._parse_command(command)
        
        try:
            # First, get a timestamp to ensure we're getting fresh results
            timestamp_cmd = "date +%s"
            timestamp_result = self._run_remote_command(self.remote_name, timestamp_cmd, timeout=5)
            check_timestamp = timestamp_result.stdout.strip() if timestamp_result.returncode == 0 else "unknown"
            
            # Create a more robust process checking script
            # Escape the command properly for the Python script
            escaped_command = command.replace("'", "\\'").replace('"', '\\"')
            
            check_script = f'''
import psutil
import json
import os
import time

def force_fresh_check():
    # Add a small delay to ensure we're not reading cached data
    time.sleep(0.1)
    
    matching_processes = []
    full_command = '{escaped_command}'
    cmd_parts = [part for part in full_command.split() if len(part) > 2]
    current_pid = os.getpid()
    primary_cmd = cmd_parts[0] if cmd_parts else ''
    
    # Get current timestamp
    check_time = time.time()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            # Skip current process and any python scripts running psutil
            if proc.info['pid'] == current_pid:
                continue
                
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline_str = ' '.join(proc.info['cmdline'])
                
                # Absolutely skip any psutil checking scripts
                if any(indicator in cmdline_str for indicator in [
                    'check_process()', 'psutil.process_iter', 'force_fresh_check',
                    'import psutil', 'def check_process'
                ]):
                    continue
                
                # Check if process was created before our check (avoid catching our own script)
                if proc.info['create_time'] and proc.info['create_time'] > check_time - 5:
                    # Process created very recently, might be our script or related
                    continue
                
                # More precise matching - require primary command and multiple parts
                matches_primary = primary_cmd in cmdline_str and primary_cmd != 'python'
                matches_parts = sum(1 for part in cmd_parts[1:] if part in cmdline_str)
                
                # Only match if we have strong evidence this is the right process
                if matches_primary and matches_parts >= 2:
                    # Additional validation: check if this looks like the actual command vs a script
                    script_indicators = ['-c', 'import ', 'def ', 'psutil']
                    is_direct_command = not any(script_indicator in cmdline_str.lower() 
                                              for script_indicator in script_indicators)
                    
                    if is_direct_command or (full_command in cmdline_str and 'python -c' not in cmdline_str):
                        matching_processes.append({{
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": proc.info['cmdline'],
                            "status": proc.info['status'],
                            "cmdline_str": cmdline_str,
                            "create_time": proc.info['create_time'],
                            "is_direct_command": is_direct_command
                        }})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return {{
        "processes": matching_processes,
        "check_timestamp": check_time,
        "search_command": full_command,
        "search_parts": cmd_parts
    }}

if __name__ == "__main__":
    result = force_fresh_check()
    print(json.dumps(result))
'''
            
            # Execute the fresh check script on remote machine
            remote_cmd = f"$HOME/venvs/ve/bin/python -c {shlex.quote(check_script)}"
            result = self._run_remote_command(self.remote_name, remote_cmd, timeout=15)
            
            if result.returncode == 0:
                try:
                    check_result = json.loads(result.stdout.strip())
                    matching_processes = check_result.get("processes", [])
                    
                    return {
                        "status": "running" if matching_processes else "not_running",
                        "running": bool(matching_processes),
                        "processes": matching_processes,
                        "command": command,
                        "tab_name": tab_name,
                        "remote": self.remote_name,
                        "check_timestamp": check_timestamp,
                        "method": "force_fresh_check"
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse fresh check output: {e}")
                    logger.error(f"Raw output was: {result.stdout}")
                    return {
                        "status": "error",
                        "error": f"Failed to parse output: {e}",
                        "running": False,
                        "command": command,
                        "tab_name": tab_name,
                        "remote": self.remote_name,
                        "raw_output": result.stdout
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
            logger.error(f"Error in fresh process check for tab '{tab_name}' on remote '{self.remote_name}': {e}")
            return {
                "status": "error",
                "error": str(e),
                "running": False,
                "command": command,
                "tab_name": tab_name,
                "remote": self.remote_name
            }

    def verify_process_alive(self, pid: int) -> bool:
        """Verify if a process with given PID is actually alive on the remote machine."""
        try:
            # Use kill -0 to check if process exists without actually killing it
            verify_cmd = f"kill -0 {pid} 2>/dev/null && echo 'alive' || echo 'dead'"
            result = self._run_remote_command(self.remote_name, verify_cmd, timeout=5)
            
            if result.returncode == 0:
                return result.stdout.strip() == 'alive'
            return False
        except Exception:
            return False

    def get_verified_process_status(self, tab_name: str) -> Dict[str, any]:
        """Get process status with additional verification that processes are actually alive."""
        # First do the fresh check
        status = self.force_fresh_process_check(tab_name)
        
        if status.get("running") and status.get("processes"):
            # Verify each process is actually alive
            verified_processes = []
            for proc in status["processes"]:
                pid = proc.get("pid")
                if pid and self.verify_process_alive(pid):
                    proc["verified_alive"] = True
                    verified_processes.append(proc)
                else:
                    proc["verified_alive"] = False
                    logger.warning(f"Process PID {pid} found in process list but not actually alive")
            
            # Update status based on verified processes
            status["processes"] = verified_processes
            status["running"] = bool(verified_processes)
            status["status"] = "running" if verified_processes else "not_running"
            status["verification_method"] = "kill_signal_check"
        
        return status

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
