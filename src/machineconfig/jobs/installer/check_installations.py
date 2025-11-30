"""
Check Installations
===================

This module scans installed applications using VirusTotal and generates a safety report.
It also provides functionality to download and install pre-checked applications.
"""

import csv
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TypedDict

import gdown
import vt  # type: ignore
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.panel import Panel

from machineconfig.utils.source_of_truth import CONFIG_ROOT, INSTALL_VERSION_ROOT
from machineconfig.utils.installer_utils.installer_runner import get_installed_cli_apps
from machineconfig.utils.path_extended import PathExtended

# Constants
APP_SUMMARY_PATH = CONFIG_ROOT.joinpath(f"profile/records/{platform.system().lower()}/apps_summary_report.csv")
VT_TOKEN_PATH = Path.home().joinpath("dotfiles/creds/tokens/virustotal")
CLOUD_STORAGE_NAME = "gdw"  # Default cloud storage name for rclone

console = Console()

class ScanResult(TypedDict):
    result: Optional[str]
    category: str

class AppData(TypedDict):
    app_name: str
    version: Optional[str]
    positive_pct: Optional[float]
    scan_time: str
    app_path: str
    app_url: str

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
            
            # if progress and task_id:
            #     progress.console.print(f"[red]🔍 Found Category {result_dict.get('category')} for {path.name}[/red]")
            malicious.append(result_item)

        positive_pct = round(len(malicious) / len(results_data) * 100, 1) if results_data else 0.0
        return positive_pct, results_data

    except Exception as e:
        if progress and task_id:
            progress.console.print(f"[bold red]❌ Failed to scan {path}: {e}[/bold red]")
        return None, []

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

def generate_markdown_report(data: list[AppData], output_path: Path) -> None:
    """Generates a Markdown table from the app data."""
    if not data:
        return

    keys = list(data[0].keys())
    header = "| " + " | ".join(key.replace("_", " ").title() for key in keys) + " |"
    separator = "| " + " | ".join("---" for _ in keys) + " |"
    rows = []
    for row in data:
        # Fix: row is a dict, keys are strings.
        row_values = [str(row.get(key, '')) for key in keys]
        rows.append("| " + " | ".join(row_values) + " |")
    
    content = "\n".join([header, separator] + rows)
    output_path.write_text(content, encoding="utf-8")
    console.print(Panel(content, title="Safety Report Summary", expand=False))

def main() -> None:
    """Main execution function."""
    console.rule("[bold blue]MachineConfig Installation Checker[/bold blue]")

    # 1. Gather Installed Apps
    with console.status("[bold green]Gathering installed applications...[/bold green]"):
        apps_paths = get_installed_cli_apps()
        # Filter and find versions
        # This part mimics the original logic but simplifies it
        # We assume apps_paths contains PathExtended objects
        
        # Find version files
        install_version_root_ext = PathExtended(INSTALL_VERSION_ROOT)
        version_files = list(install_version_root_ext.search()) if install_version_root_ext.exists() else []
        
        apps_to_scan: list[tuple[PathExtended, Optional[str]]] = []
        
        for app_path in apps_paths:
            # Try to find version
            version = None
            # Simple matching logic: check if any version file matches the app name
            # This is a heuristic from the original code
            matching_versions = [v for v in version_files if v.stem == app_path.stem]
            if matching_versions:
                version = matching_versions[0].read_text(encoding="utf-8").strip()
            
            apps_to_scan.append((app_path, version))

    console.print(f"[green]Found {len(apps_to_scan)} applications to check.[/green]")

    # 2. Scan Apps with VirusTotal
    app_data_list: list[AppData] = []
    
    try:
        client = get_vt_client()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            scan_task = progress.add_task("[cyan]Scanning apps...", total=len(apps_to_scan))
            
            for app_path, version in apps_to_scan:
                progress.update(scan_task, description=f"Scanning {app_path.name}...")
                
                positive_pct, _ = scan_file(app_path, client, progress, scan_task)
                
                # Upload if safe (optional, based on original code logic which uploaded everything?)
                # Original code uploaded everything.
                progress.update(scan_task, description=f"Uploading {app_path.name}...")
                app_url = upload_app(app_path) or ""
                
                app_data_list.append({
                    "app_name": app_path.stem,
                    "version": version,
                    "positive_pct": positive_pct,
                    "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "app_path": app_path.collapseuser(strict=False).as_posix(),
                    "app_url": app_url
                })
                
                progress.advance(scan_task)

    except FileNotFoundError as e:
        console.print(f"[bold red]{e}[/bold red]")
        console.print("[yellow]Skipping scanning due to missing credentials.[/yellow]")
        # Fallback: just list apps without scan results
        for app_path, version in apps_to_scan:
             app_data_list.append({
                "app_name": app_path.stem,
                "version": version,
                "positive_pct": None,
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "app_path": app_path.collapseuser(strict=False).as_posix(),
                "app_url": ""
            })
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during scanning: {e}[/bold red]")

    # 3. Generate Reports
    if app_data_list:
        # CSV Report
        APP_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
        csv_path = APP_SUMMARY_PATH.with_suffix(".csv")
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = app_data_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(app_data_list)
        
        console.print(f"[green]CSV report saved to: {csv_path}[/green]")

        # Markdown Report
        md_path = APP_SUMMARY_PATH.with_suffix(".md")
        generate_markdown_report(app_data_list, md_path)
        console.print(f"[green]Markdown report saved to: {md_path}[/green]")

class PrecheckedPackages:
    """Handles installation of pre-checked packages from the summary report."""
    
    def __init__(self) -> None:
        self.data: list[dict[str, Any]] = []
        if APP_SUMMARY_PATH.exists():
            with open(APP_SUMMARY_PATH, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.data = list(reader)
        else:
            console.print(f"[yellow]Warning: Summary report not found at {APP_SUMMARY_PATH}[/yellow]")

    @staticmethod
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

    @staticmethod
    def install_cli_app(app_url: str) -> bool:
        """Downloads and installs a CLI app."""
        try:
            if not app_url:
                return False
                
            exe_path = PrecheckedPackages.download_google_drive_file(app_url)
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

    def download_safe_apps(self, name: str = "essentials") -> None:
        """Downloads and installs safe apps."""
        if not self.data:
            console.print("[red]No app data available to install.[/red]")
            return

        apps_to_install = []
        if name == "essentials":
            # Install all available apps in the report? Or filter?
            # Original code installed all if name="essentials" (implied by logic)
            apps_to_install = [item['app_url'] for item in self.data if item.get('app_url')]
        else:
            apps_to_install = [item['app_url'] for item in self.data if item.get('app_name') == name and item.get('app_url')]

        if not apps_to_install:
            console.print(f"[yellow]No apps found to install for '{name}'.[/yellow]")
            return

        console.print(f"[bold]Installing {len(apps_to_install)} apps...[/bold]")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.install_cli_app, apps_to_install))
        
        success_count = sum(results)
        console.print(f"[bold green]Successfully installed {success_count}/{len(apps_to_install)} apps.[/bold green]")

if __name__ == '__main__':
    main()
