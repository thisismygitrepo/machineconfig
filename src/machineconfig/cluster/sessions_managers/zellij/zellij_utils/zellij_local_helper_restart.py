#!/usr/bin/env python3
import subprocess
import time
import logging
from rich.console import Console

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig


logger = logging.getLogger(__name__)
console = Console()


def restart_tab_process(tab_name: str, layout_config: LayoutConfig, session_name: str) -> bool:
    """Restart the process running in a specific Zellij tab without changing the layout.
    
    This function will:
    1. Navigate to the specified tab
    2. Send Ctrl+C to stop the running process
    3. Clear the screen
    4. Re-execute the original command
    
    The tab layout and configuration remain unchanged - only the process is restarted.
    """
    if not layout_config:
        logger.error("No layout config available. Cannot restart tab.")
        return False
    
    tab_config = None
    for tab in layout_config["layoutTabs"]:
        if tab["tabName"] == tab_name:
            tab_config = tab
            break
    
    if tab_config is None:
        logger.error(f"Tab '{tab_name}' not found in layout config.")
        console.print(f"[bold red]❌ Tab '{tab_name}' not found in layout[/bold red]")
        return False
    
    command = tab_config.get("command", "")
    if not command:
        logger.warning(f"No command configured for tab '{tab_name}'")
        console.print(f"[bold yellow]⚠️  No command to restart for tab '{tab_name}'[/bold yellow]")
        return False
    
    console.print(f"[bold cyan]🔄 Restarting tab[/bold cyan] [yellow]'{tab_name}'[/yellow]")
    console.print(f"[dim]Command: {command}[/dim]")
    
    try:
        session_arg = f"--session {session_name}" if session_name else ""
        
        subprocess.run(f"zellij {session_arg} action go-to-tab-name '{tab_name}'", shell=True, check=True, capture_output=True, text=True)
        time.sleep(0.5)
        
        subprocess.run(f"zellij {session_arg} action write-chars '\\u0003'", shell=True, check=True, capture_output=True, text=True)
        time.sleep(0.3)
        
        subprocess.run(f"zellij {session_arg} action write-chars 'clear'", shell=True, check=True, capture_output=True, text=True)
        subprocess.run(f"zellij {session_arg} action write-chars '\\n'", shell=True, check=True, capture_output=True, text=True)
        time.sleep(0.2)
        
        escaped_command = command.replace("'", "'\\''")
        subprocess.run(f"zellij {session_arg} action write-chars '{escaped_command}'", shell=True, check=True, capture_output=True, text=True)
        subprocess.run(f"zellij {session_arg} action write-chars '\\n'", shell=True, check=True, capture_output=True, text=True)
        
        console.print(f"[bold green]✅ Tab '{tab_name}' restarted successfully[/bold green]")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restart tab '{tab_name}': {e}")
        console.print(f"[bold red]❌ Failed to restart tab '{tab_name}'[/bold red]")
        console.print(f"[red]Error: {e}[/red]")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while restarting tab '{tab_name}': {e}")
        console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")
        return False
