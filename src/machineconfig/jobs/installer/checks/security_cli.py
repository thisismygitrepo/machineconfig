
from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from machineconfig.jobs.installer.checks.check_installations import APP_SUMMARY_PATH, collect_apps_to_scan, scan_and_write_reports
from machineconfig.jobs.installer.checks.install_utils import download_google_drive_file, download_safe_apps, load_summary_report, upload_app
from machineconfig.jobs.installer.checks.report_utils import AppData, generate_markdown_report
from machineconfig.jobs.installer.checks.vt_utils import get_vt_client, scan_file
from machineconfig.utils.path_extended import PathExtended

console = Console()


def _parse_apps_csv(apps_csv: str) -> list[str]:
    return [name.strip() for name in apps_csv.split(",") if name.strip()]


def _parse_positive_pct(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or cleaned.lower() == "none":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _to_app_data_list(rows: list[dict[str, object]]) -> list[AppData]:
    app_data_list: list[AppData] = []
    for row in rows:
        app_name = str(row.get("app_name", ""))
        version_raw = row.get("version")
        version = str(version_raw) if version_raw not in {None, ""} else None
        positive_pct = _parse_positive_pct(str(row.get("positive_pct", "")))
        scan_time = str(row.get("scan_time", ""))
        app_path = str(row.get("app_path", ""))
        app_url = str(row.get("app_url", ""))
        app_data_list.append(
            {
                "app_name": app_name,
                "version": version,
                "positive_pct": positive_pct,
                "scan_time": scan_time,
                "app_path": app_path,
                "app_url": app_url,
            }
        )
    return app_data_list


def scan_all() -> None:
    scan_and_write_reports(None)


def scan_apps(apps: Annotated[str, typer.Argument(..., help="Comma-separated app names to scan")]) -> None:
    app_names = _parse_apps_csv(apps)
    scan_and_write_reports(app_names)


def list_all() -> None:
    apps_to_scan = collect_apps_to_scan(None)
    table = Table(title="Installed CLI Apps", show_lines=False)
    table.add_column("Name")
    table.add_column("Version", justify="right")
    table.add_column("Path")
    for app_path, version in apps_to_scan:
        table.add_row(app_path.stem, version or "", app_path.collapseuser(strict=False).as_posix())
    console.print(table)


def list_apps(apps: Annotated[str, typer.Argument(..., help="Comma-separated app names to list")]) -> None:
    app_names = _parse_apps_csv(apps)
    apps_to_scan = collect_apps_to_scan(app_names)
    table = Table(title="Installed CLI Apps", show_lines=False)
    table.add_column("Name")
    table.add_column("Version", justify="right")
    table.add_column("Path")
    for app_path, version in apps_to_scan:
        table.add_row(app_path.stem, version or "", app_path.collapseuser(strict=False).as_posix())
    console.print(table)


def upload(path: Annotated[Path, typer.Argument(..., help="Path to a local file to upload")]) -> None:
    link = upload_app(PathExtended(path))
    if not link:
        raise typer.Exit(code=1)
    console.print(link)


def download(url: Annotated[str, typer.Argument(..., help="Google Drive URL or file id")]) -> None:
    path = download_google_drive_file(url)
    console.print(path.as_posix())


def install(name: Annotated[str, typer.Argument(..., help="App name from summary report or 'essentials'")]) -> None:
    download_safe_apps(name)


def summary() -> None:
    rows = load_summary_report()
    if not rows:
        raise typer.Exit(code=1)
    app_data_list = _to_app_data_list(rows)
    scanned = [row for row in app_data_list if row.get("positive_pct") is not None]
    clean = [row for row in scanned if row.get("positive_pct") == 0.0]
    console.print(f"Apps in report: {len(app_data_list)}")
    console.print(f"Scanned: {len(scanned)}")
    console.print(f"Clean (0%): {len(clean)}")
    console.print(f"Report CSV: {APP_SUMMARY_PATH.with_suffix('.csv')}")
    console.print(f"Report MD: {APP_SUMMARY_PATH.with_suffix('.md')}")


def report() -> None:
    rows = load_summary_report()
    if not rows:
        raise typer.Exit(code=1)
    app_data_list = _to_app_data_list(rows)
    md_path = APP_SUMMARY_PATH.with_suffix(".md")
    generate_markdown_report(app_data_list, md_path)
    console.print(f"Markdown report saved to: {md_path}")


def scan_path(path: Annotated[Path, typer.Argument(..., help="Path to a file to scan")]) -> None:
    try:
        client = get_vt_client()
    except FileNotFoundError as e:
        console.print(f"[bold red]{e}[/bold red]")
        raise typer.Exit(code=1)
    positive_pct, _ = scan_file(PathExtended(path), client)
    console.print(f"{path.name}: {positive_pct}% positives")


def get_app() -> typer.Typer:
    app = typer.Typer(
        name="security-cli",
        help="Security related CLI tools.",
        no_args_is_help=True,
        add_help_option=True,
        add_completion=False,
    )

    app.command(name="scan-all", help="Scan all installed apps and generate reports")(scan_all)
    app.command(name="scan", help="Scan comma-separated app names and generate reports")(scan_apps)
    app.command(name="list-all", help="List all installed apps")(list_all)
    app.command(name="list", help="List comma-separated app names")(list_apps)
    app.command(name="upload", help="Upload a local file to cloud storage")(upload)
    app.command(name="download", help="Download a file from Google Drive")(download)
    app.command(name="install", help="Install safe apps from summary report")(install)
    app.command(name="summary", help="Show summary statistics for the last report")(summary)
    app.command(name="report", help="Regenerate Markdown report from CSV summary")(report)
    app.command(name="scan-path", help="Scan a single file path with VirusTotal")(scan_path)

    return app
