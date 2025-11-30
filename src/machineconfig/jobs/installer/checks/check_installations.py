"""
Check Installations
===================

This module scans installed applications using VirusTotal and generates a safety report.
It also provides functionality to download and install pre-checked applications.
"""

import csv
import platform
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from machineconfig.jobs.installer.checks.install_utils import upload_app
from machineconfig.jobs.installer.checks.report_utils import AppData, generate_markdown_report
from machineconfig.jobs.installer.checks.vt_utils import get_vt_client, scan_file
from machineconfig.utils.installer_utils.installer_runner import get_installed_cli_apps
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import CONFIG_ROOT, INSTALL_VERSION_ROOT

# Constants
APP_SUMMARY_PATH = CONFIG_ROOT.joinpath(f"profile/records/{platform.system().lower()}/apps_summary_report.csv")

console = Console()

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
            fieldnames = list(app_data_list[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(app_data_list)
        
        console.print(f"[green]CSV report saved to: {csv_path}[/green]")

        # Markdown Report
        md_path = APP_SUMMARY_PATH.with_suffix(".md")
        generate_markdown_report(app_data_list, md_path)
        console.print(f"[green]Markdown report saved to: {md_path}[/green]")



if __name__ == '__main__':
    main()
