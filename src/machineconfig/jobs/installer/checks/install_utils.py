"""
Installation Utilities
======================

This module provides functionality to download and install pre-checked applications.
"""

import csv
import platform
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import gdown
from rich.console import Console

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import CONFIG_ROOT

# Constants
APP_SUMMARY_PATH = CONFIG_ROOT.joinpath(f"profile/records/{platform.system().lower()}/apps_summary_report.csv")
CLOUD_STORAGE_NAME = "gdw"  # Default cloud storage name for rclone

console = Console()

def upload_app(path: PathExtended) -> Optional[str]:
    """Uploads the app to cloud storage and returns the shareable link."""
    try:
        # Using PathExtended.to_cloud
        # Assuming 'gdw' is the configured remote in rclone
        link_path = path.to_cloud(CLOUD_STORAGE_NAME, rel2home=True, share=True, os_specific=True, verbose=False)
        if link_path:
             return str(link_path)
        return None
    except Exception as e:
        console.print(f"[red]Failed to upload {path}: {e}[/red]")
        return None

def download_google_drive_file(url: str) -> PathExtended:
    """Downloads a file from Google Drive using gdown."""
    try:
        # Extract ID from URL
        # Assuming URL format like https://drive.google.com/file/d/FILE_ID/view or similar
        # or https://drive.google.com/uc?id=FILE_ID
        if "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        elif "/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
        else:
            # Fallback to gdown's auto detection or just pass URL
            file_id = url

        # Create a temporary directory for download
        output_dir = PathExtended.tmpdir(prefix="gdown_")
        # gdown.download returns the output filename
        output_file = gdown.download(id=file_id, output=str(output_dir) + "/", quiet=False, fuzzy=True)
        
        if not output_file:
            raise ValueError(f"Download failed for {url}")
            
        return PathExtended(output_file)
    except Exception as e:
        raise RuntimeError(f"Failed to download from Google Drive: {e}") from e

def install_cli_app(app_url: str) -> bool:
    """Downloads and installs a CLI app."""
    try:
        if not app_url:
            return False
            
        exe_path = download_google_drive_file(app_url)
        console.print(f"[green]Downloaded {exe_path.name}[/green]")
        
        system = platform.system().lower()
        if system in ["linux", "darwin"]:
            exe_path.chmod(0o755) # Make executable
            # Move to local bin (requires user to have write access or sudo, which we can't easily do here without interaction)
            # Using ~/.local/bin is safer
            install_path = Path.home() / ".local/bin"
            install_path.mkdir(parents=True, exist_ok=True)
            target = install_path / exe_path.name
            exe_path.rename(target)
            console.print(f"[green]Installed to {target}[/green]")
        elif system == "windows":
            install_path = Path.home() / "AppData/Local/Microsoft/WindowsApps"
            install_path.mkdir(parents=True, exist_ok=True)
            target = install_path / exe_path.name
            # Use shutil.move or PathExtended.move
            exe_path.move(path=target, overwrite=True)
            console.print(f"[green]Installed to {target}[/green]")
        
        return True
    except Exception as e:
        console.print(f"[red]Failed to install app from {app_url}: {e}[/red]")
        return False

def load_summary_report() -> list[dict[str, Any]]:
    """Loads the summary report from CSV."""
    if APP_SUMMARY_PATH.exists():
        with open(APP_SUMMARY_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    else:
        console.print(f"[yellow]Warning: Summary report not found at {APP_SUMMARY_PATH}[/yellow]")
        return []

def download_safe_apps(name: str = "essentials") -> None:
    """Downloads and installs safe apps."""
    data = load_summary_report()
    if not data:
        console.print("[red]No app data available to install.[/red]")
        return

    apps_to_install = []
    if name == "essentials":
        # Install all available apps in the report? Or filter?
        # Original code installed all if name="essentials" (implied by logic)
        apps_to_install = [item['app_url'] for item in data if item.get('app_url')]
    else:
        apps_to_install = [item['app_url'] for item in data if item.get('app_name') == name and item.get('app_url')]

    if not apps_to_install:
        console.print(f"[yellow]No apps found to install for '{name}'.[/yellow]")
        return

    console.print(f"[bold]Installing {len(apps_to_install)} apps...[/bold]")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(install_cli_app, apps_to_install))
    
    success_count = sum(results)
    console.print(f"[bold green]Successfully installed {success_count}/{len(apps_to_install)} apps.[/bold green]")
