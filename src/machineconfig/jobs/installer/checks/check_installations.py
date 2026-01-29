"""
Check Installations
===================

This module scans installed applications using VirusTotal and generates a safety report.
It also provides functionality to download and install pre-checked applications.
"""

import csv
import platform
from datetime import datetime
from pathlib import Path
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


def _normalize_app_names(app_names: list[str]) -> list[str]:
    return [name.strip().lower() for name in app_names if name.strip()]


def _build_version_lookup() -> dict[str, str]:
    install_version_root_ext = PathExtended(INSTALL_VERSION_ROOT)
    version_files = list(install_version_root_ext.search()) if install_version_root_ext.exists() else []
    versions: dict[str, str] = {}
    for version_file in version_files:
        versions[version_file.stem] = version_file.read_text(encoding="utf-8").strip()
    return versions


def collect_apps_to_scan(app_names: list[str] | None) -> list[tuple[PathExtended, Optional[str]]]:
    with console.status("[bold green]Gathering installed applications...[/bold green]"):
        apps_paths = get_installed_cli_apps()
        if app_names is not None:
            normalized = set(_normalize_app_names(app_names))
            apps_paths = [app_path for app_path in apps_paths if app_path.stem.lower() in normalized]
        versions = _build_version_lookup()
        apps_to_scan: list[tuple[PathExtended, Optional[str]]] = []
        for app_path in apps_paths:
            version = versions.get(app_path.stem)
            apps_to_scan.append((app_path, version))
    return apps_to_scan


def scan_apps_with_vt(apps_to_scan: list[tuple[PathExtended, Optional[str]]]) -> list[AppData]:
    app_data_list: list[AppData] = []
    if not apps_to_scan:
        return app_data_list
    try:
        client = get_vt_client()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            scan_task = progress.add_task("[cyan]Scanning apps...", total=len(apps_to_scan))
            for app_path, version in apps_to_scan:
                progress.update(scan_task, description=f"Scanning {app_path.name}...")
                positive_pct, _ = scan_file(app_path, client, progress, scan_task)
                progress.update(scan_task, description=f"Uploading {app_path.name}...")
                app_url = upload_app(app_path) or ""
                app_data_list.append(
                    {
                        "app_name": app_path.stem,
                        "version": version,
                        "positive_pct": positive_pct,
                        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "app_path": app_path.collapseuser(strict=False).as_posix(),
                        "app_url": app_url,
                    }
                )
                progress.advance(scan_task)
    except FileNotFoundError as e:
        console.print(f"[bold red]{e}[/bold red]")
        console.print("[yellow]Skipping scanning due to missing credentials.[/yellow]")
        for app_path, version in apps_to_scan:
            app_data_list.append(
                {
                    "app_name": app_path.stem,
                    "version": version,
                    "positive_pct": None,
                    "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "app_path": app_path.collapseuser(strict=False).as_posix(),
                    "app_url": "",
                }
            )
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during scanning: {e}[/bold red]")
    return app_data_list


def write_reports(app_data_list: list[AppData]) -> tuple[Path, Path]:
    if not app_data_list:
        raise ValueError("No app data available to write reports.")
    APP_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    csv_path = APP_SUMMARY_PATH.with_suffix(".csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = list(app_data_list[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(app_data_list)
    md_path = APP_SUMMARY_PATH.with_suffix(".md")
    generate_markdown_report(app_data_list, md_path)
    return csv_path, md_path


def scan_and_write_reports(app_names: list[str] | None) -> list[AppData]:
    console.rule("[bold blue]MachineConfig Installation Checker[/bold blue]")
    apps_to_scan = collect_apps_to_scan(app_names)
    console.print(f"[green]Found {len(apps_to_scan)} applications to check.[/green]")
    app_data_list = scan_apps_with_vt(apps_to_scan)
    if app_data_list:
        csv_path, md_path = write_reports(app_data_list)
        console.print(f"[green]CSV report saved to: {csv_path}[/green]")
        console.print(f"[green]Markdown report saved to: {md_path}[/green]")
    return app_data_list


def main() -> None:
    scan_and_write_reports(None)


if __name__ == "__main__":
    main()
