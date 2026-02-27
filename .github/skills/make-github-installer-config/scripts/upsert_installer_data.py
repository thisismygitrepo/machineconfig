from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import argparse
import json
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely upsert one installer entry into installer_data.json.")
    parser.add_argument("--installer-data", required=False, default="src/machineconfig/jobs/installer/installer_data.json", help="Path to installer_data.json")
    parser.add_argument("--entry-json", required=True, help="Path to JSON produced by build_installer_config.py (contains {entry, checks})")
    parser.add_argument("--dry-run", action="store_true", help="Show action but do not write")
    parser.add_argument("--fail-on-check-warnings", action="store_true", help="Abort if build checks contain warnings")
    return parser


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    installer_path = Path(str(args.installer_data)).expanduser().resolve()
    entry_path = Path(str(args.entry_json)).expanduser().resolve()
    dry_run: bool = bool(args.dry_run)
    fail_on_check_warnings: bool = bool(args.fail_on_check_warnings)

    if installer_path.exists() is False:
        raise FileNotFoundError(f"installer_data path not found: {installer_path}")
    if entry_path.exists() is False:
        raise FileNotFoundError(f"entry JSON path not found: {entry_path}")

    installer_payload: Any = load_json(installer_path)
    generated_payload: Any = load_json(entry_path)

    if not isinstance(installer_payload, dict):
        raise ValueError("installer_data root must be object")
    installers_any: Any = installer_payload.get("installers")
    if not isinstance(installers_any, list):
        raise ValueError("installer_data.installers must be an array")

    if not isinstance(generated_payload, dict):
        raise ValueError("entry JSON root must be object")
    entry_any: Any = generated_payload.get("entry")
    checks_any: Any = generated_payload.get("checks", {})
    if not isinstance(entry_any, dict):
        raise ValueError("entry JSON must include object key: entry")

    app_name_any: Any = entry_any.get("appName")
    repo_url_any: Any = entry_any.get("repoURL")
    if not isinstance(app_name_any, str) or len(app_name_any.strip()) == 0:
        raise ValueError("entry.appName must be non-empty string")
    if not isinstance(repo_url_any, str) or len(repo_url_any.strip()) == 0:
        raise ValueError("entry.repoURL must be non-empty string")

    warning_rows: list[str] = []
    if isinstance(checks_any, dict):
        latest_checks_any: Any = checks_any.get("latestPatternChecks")
        if isinstance(latest_checks_any, list):
            for item in latest_checks_any:
                if isinstance(item, str):
                    warning_rows.append(item)

    if fail_on_check_warnings and len(warning_rows) > 0:
        raise RuntimeError("Refusing upsert because latestPatternChecks is non-empty")

    matched_indices: list[int] = []
    for idx, row in enumerate(installers_any):
        if not isinstance(row, dict):
            continue
        row_app: Any = row.get("appName")
        row_repo: Any = row.get("repoURL")
        if row_app == app_name_any or row_repo == repo_url_any:
            matched_indices.append(idx)

    action: str
    if len(matched_indices) == 0:
        installers_any.append(entry_any)
        action = "append"
    else:
        first_idx: int = matched_indices[0]
        installers_any[first_idx] = entry_any
        action = f"update index {first_idx}"
        if len(matched_indices) > 1:
            dedupe_indices: list[int] = matched_indices[1:]
            for idx in sorted(dedupe_indices, reverse=True):
                installers_any.pop(idx)
            action = action + f" and removed {len(dedupe_indices)} duplicate(s)"

    if dry_run:
        sys.stdout.write(f"Dry run: would {action} in {installer_path}\n")
        if len(warning_rows) > 0:
            sys.stdout.write("Warnings:\n")
            for warning in warning_rows:
                sys.stdout.write(f"- {warning}\n")
        return

    backup_suffix: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = installer_path.with_suffix(installer_path.suffix + f".{backup_suffix}.bak")
    backup_path.write_text(installer_path.read_text(encoding="utf-8"), encoding="utf-8")

    installer_path.write_text(json.dumps(installer_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote installer data via {action}: {installer_path}\n")
    sys.stdout.write(f"Backup written: {backup_path}\n")
    if len(warning_rows) > 0:
        sys.stdout.write("Warnings:\n")
        for warning in warning_rows:
            sys.stdout.write(f"- {warning}\n")


if __name__ == "__main__":
    main()
