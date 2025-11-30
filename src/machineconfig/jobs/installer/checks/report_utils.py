"""
Report Utilities
================

This module provides functionality to generate reports for installed applications.
"""

from pathlib import Path
from typing import Optional, TypedDict
from rich.console import Console
from rich.panel import Panel

console = Console()

class AppData(TypedDict):
    app_name: str
    version: Optional[str]
    positive_pct: Optional[float]
    scan_time: str
    app_path: str
    app_url: str

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
