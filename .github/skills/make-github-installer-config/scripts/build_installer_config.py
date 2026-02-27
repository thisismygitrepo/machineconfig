from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import argparse
import json
import sys

from skill_lib import classify_arch
from skill_lib import classify_os
from skill_lib import fetch_releases
from skill_lib import file_exists_for_pattern
from skill_lib import looks_like_binary_asset
from skill_lib import parse_repo_url
from skill_lib import to_placeholder_pattern


PLATFORMS: tuple[str, ...] = ("linux", "macos", "windows")
ARCHES: tuple[str, ...] = ("amd64", "arm64")


def infer_best_pattern(candidates: list[str], os_name: str) -> str | None:
    if len(candidates) == 0:
        return None
    counts: Counter[str] = Counter(candidates)
    ranked: list[tuple[str, int]] = sorted(counts.items(), key=lambda row: row[1], reverse=True)

    if os_name == "linux":
        musl_first: list[tuple[str, int]] = [item for item in ranked if "musl" in item[0].lower()]
        if len(musl_first) > 0:
            return musl_first[0][0]
    return ranked[0][0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build installer_data.json config entry from GitHub release assets.")
    parser.add_argument("--repo-url", required=True, help="GitHub repository URL")
    parser.add_argument("--app-name", required=True, help="Lowercase app name")
    parser.add_argument("--doc", required=True, help="Short description")
    parser.add_argument("--limit", required=False, default=8, type=int, help="Number of releases to inspect")
    parser.add_argument("--output", required=False, default="-", help="Output path for JSON object, or '-' for stdout")
    parser.add_argument("--strict-latest-check", action="store_true", help="Fail if any non-null pattern does not match latest release assets")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repo_url: str = str(args.repo_url)
    app_name: str = str(args.app_name).strip().lower()
    doc: str = str(args.doc).strip()
    limit: int = int(args.limit)
    output: str = str(args.output)
    strict_latest_check: bool = bool(args.strict_latest_check)

    if len(app_name) == 0:
        raise ValueError("--app-name cannot be empty")
    if len(doc) == 0:
        raise ValueError("--doc cannot be empty")

    spec = parse_repo_url(repo_url=repo_url)
    releases = fetch_releases(spec=spec, limit=limit)
    latest_release = releases[0]
    latest_asset_names: set[str] = {asset.name for asset in latest_release.assets}

    buckets: dict[str, dict[str, list[str]]] = {arch: {platform: [] for platform in PLATFORMS} for arch in ARCHES}

    for release in releases:
        for asset in release.assets:
            if looks_like_binary_asset(asset_name=asset.name) is False:
                continue
            os_name: str | None = classify_os(asset_name=asset.name)
            arch_name: str | None = classify_arch(asset_name=asset.name)
            if os_name is None or arch_name is None:
                continue
            pattern: str = to_placeholder_pattern(asset_name=asset.name, tag_name=release.tag_name)
            buckets[arch_name][os_name].append(pattern)

    pattern_matrix: dict[str, dict[str, str | None]] = {
        arch: {platform: infer_best_pattern(candidates=buckets[arch][platform], os_name=platform) for platform in PLATFORMS}
        for arch in ARCHES
    }

    failed_checks: list[str] = []
    for arch in ARCHES:
        for platform in PLATFORMS:
            pattern = pattern_matrix[arch][platform]
            if pattern is None:
                continue
            exists: bool = file_exists_for_pattern(asset_names=latest_asset_names, pattern=pattern, latest_tag_name=latest_release.tag_name)
            if exists is False:
                failed_checks.append(f"Missing latest asset for {arch}/{platform}: pattern='{pattern}' tag='{latest_release.tag_name}'")

    if strict_latest_check and len(failed_checks) > 0:
        raise RuntimeError("; ".join(failed_checks))

    entry: dict[str, Any] = {
        "appName": app_name,
        "repoURL": repo_url,
        "doc": doc,
        "fileNamePattern": pattern_matrix,
    }

    output_payload: dict[str, Any] = {
        "entry": entry,
        "checks": {
            "latestTag": latest_release.tag_name,
            "latestAssetCount": len(latest_asset_names),
            "latestPatternChecks": failed_checks,
        },
    }

    out_text: str = json.dumps(output_payload, indent=2, ensure_ascii=False)
    if output == "-":
        sys.stdout.write(out_text + "\n")
        return

    out_path = Path(output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote config output to: {out_path}\n")


if __name__ == "__main__":
    main()
