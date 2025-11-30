"""
VirusTotal Utilities
====================

This module provides functionality to interact with VirusTotal API.
"""

import time
from pathlib import Path
from typing import Any, Optional, TypedDict

import vt
from rich.progress import Progress, TaskID

# Constants
VT_TOKEN_PATH = Path.home().joinpath("dotfiles/creds/tokens/virustotal")

class ScanResult(TypedDict):
    result: Optional[str]
    category: str

def get_vt_client() -> vt.Client:
    """Retrieves the VirusTotal client using the token from the credentials file."""
    if not VT_TOKEN_PATH.exists():
        raise FileNotFoundError(f"VirusTotal token not found at {VT_TOKEN_PATH}")
    
    token = VT_TOKEN_PATH.read_text(encoding="utf-8").split("\n")[0].strip()
    return vt.Client(token)

def scan_file(path: Path, client: vt.Client, progress: Optional[Progress] = None, task_id: Optional[TaskID] = None) -> tuple[Optional[float], list[Any]]:
    """
    Scans a file using VirusTotal.
    
    Args:
        path: Path to the file to scan.
        client: VirusTotal client instance.
        progress: Optional Rich progress bar.
        task_id: Optional Task ID for the progress bar.

    Returns:
        A tuple containing the positive percentage (0-100) and the list of result details.
        Returns (None, []) if scanning fails or file is skipped.
    """
    if path.is_dir():
        if progress and task_id:
            progress.console.print(f"[yellow]📁 Skipping directory: {path}[/yellow]")
        return None, []

    try:
        with open(path, "rb") as f:
            analysis = client.scan_file(f)
        
        repeat_counter = 0
        while True:
            try:
                anal = client.get_object("/analyses/{}", analysis.id)
                if anal.status == "completed":
                    break
            except Exception as e:
                repeat_counter += 1
                if repeat_counter > 3:
                    raise ValueError(f"❌ Error scanning {path}: {e}") from e
                if progress and task_id:
                    progress.console.print(f"[red]⚠️  Error scanning {path}, retrying... ({repeat_counter}/3)[/red]")
                time.sleep(5)
            
            time.sleep(10) # Wait before checking status again

        # Process results
        results_data = list(anal.results.values())
        malicious = []
        for result_item in results_data:
            result_dict = result_item.__dict__ if hasattr(result_item, '__dict__') else {
                'result': getattr(result_item, 'result', None),
                'category': getattr(result_item, 'category', 'unknown')
            }

            if result_dict.get('result') is None and result_dict.get('category') in ["undetected", "type-unsupported", "failure", "timeout", "confirmed-timeout"]:
                continue
            
            malicious.append(result_item)

        positive_pct = round(len(malicious) / len(results_data) * 100, 1) if results_data else 0.0
        return positive_pct, results_data

    except Exception as e:
        if progress and task_id:
            progress.console.print(f"[bold red]❌ Failed to scan {path}: {e}[/bold red]")
        return None, []
