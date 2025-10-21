#!/usr/bin/env python3
"""
Enhanced command execution utilities with Rich formatting for better user experience.
"""

import subprocess
import re
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()


def run_enhanced_command(command: str, description: Optional[str], show_progress: bool, timeout: Optional[int]) -> Dict[str, Any]:
    """
    Run a command with enhanced Rich formatting and user feedback.

    Args:
        command: The command to execute
        description: Optional description for progress display
        show_progress: Whether to show a progress spinner
        timeout: Optional timeout in seconds

    Returns:
        Dictionary with success status, output, and error information
    """

    if description is None:
        description = f"Executing: {command[:50]}..."

    try:
        if show_progress:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=True) as progress:
                task = progress.add_task(f"[cyan]{description}[/cyan]", total=None)

                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)

                progress.update(task, completed=True)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)

        # Enhanced output processing
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""

        # Process common Zellij messages with enhanced formatting
        if "Session:" in stdout and "successfully deleted" in stdout:
            session_match = re.search(r'Session: "([^"]+)" successfully deleted', stdout)
            if session_match:
                session_name = session_match.group(1)
                console.print(f"[bold red]🗑️  Session[/bold red] [yellow]'{session_name}'[/yellow] [red]successfully deleted[/red]")

        if "zellij layout is running" in stdout:
            console.print(stdout.replace("zellij layout is running @", "[bold green]🚀 Zellij layout is running[/bold green] [yellow]@[/yellow]"))

        # Handle pseudo-terminal warnings with less alarming appearance
        if "Pseudo-terminal will not be allocated" in stderr:
            console.print("[dim yellow]ℹ️  Note: Running in non-interactive mode[/dim yellow]")
            stderr = stderr.replace("Pseudo-terminal will not be allocated because stdin is not a terminal.\n", "")

        if result.returncode == 0:
            if stdout and not any(msg in stdout for msg in ["Session:", "zellij layout is running"]):
                console.print(f"[green]{stdout}[/green]")
            return {"success": True, "returncode": result.returncode, "stdout": stdout, "stderr": stderr}
        else:
            if stderr:
                console.print(f"[bold red]Error:[/bold red] [red]{stderr}[/red]")
            return {"success": False, "returncode": result.returncode, "stdout": stdout, "stderr": stderr}

    except subprocess.TimeoutExpired:
        console.print(f"[bold red]⏰ Command timed out after {timeout} seconds[/bold red]")
        return {"success": False, "error": "Timeout", "timeout": timeout}
    except Exception as e:
        console.print(f"[bold red]💥 Unexpected error:[/bold red] [red]{str(e)}[/red]")
        return {"success": False, "error": str(e)}


def enhanced_zellij_session_start(session_name: str, layout_path: str) -> Dict[str, Any]:
    """
    Start a Zellij session with enhanced visual feedback.
    """
    console.print()
    console.print(Panel.fit(f"🚀 Starting Zellij Session: [bold cyan]{session_name}[/bold cyan]", style="green", box=box.ROUNDED))
    # Delete existing session first (suppress normal output)
    delete_cmd = f"zellij delete-session --force {session_name}"
    run_enhanced_command(
        delete_cmd,
        f"Cleaning up existing session '{session_name}'",
        False,
        5,  # Quick timeout for cleanup
    )
    # Start new session (use -b for background to avoid hanging)
    start_cmd = f"zellij --layout {layout_path} a -b {session_name}"
    start_result = run_enhanced_command(
        command=start_cmd, description=f"Starting session '{session_name}' with layout", show_progress=False,
        timeout=10,  # Add timeout to prevent hanging
    )
    if start_result["success"]:
        console.print(Panel(f"[bold green]✅ Session '{session_name}' is now running![/bold green]\n[dim]Layout: {layout_path}[/dim]", style="green", title="🎉 Success"))
    else:
        console.print(Panel(f"[bold red]❌ Failed to start session '{session_name}'[/bold red]\n[red]{start_result.get('stderr', 'Unknown error')}[/red]", style="red", title="💥 Error"))
    # print("Sleeping for 3 seconds to allow zellij to initialize...")
    # time.sleep(3)  # Brief pause for readability
    return start_result


if __name__ == "__main__":
    # Demo the enhanced command execution
    console.print(Panel.fit("🎨 Enhanced Command Execution Demo", style="bold cyan"))

    # Test with a simple command
    result = run_enhanced_command("echo 'Hello, Rich world!'", "Testing enhanced output", True, None)
    console.print(f"Result: {result}")
