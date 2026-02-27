

from pathlib import Path
from typing import Any
import argparse
import json
import sys

from skill_lib import classify_arch
from skill_lib import classify_os
from skill_lib import fetch_releases
from skill_lib import looks_like_binary_asset
from skill_lib import parse_repo_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan GitHub releases and classify binary assets by platform/arch.")
    parser.add_argument("--repo-url", required=True, help="GitHub repository URL, e.g. https://github.com/owner/repo")
    parser.add_argument("--limit", required=False, default=8, type=int, help="Number of recent releases to inspect")
    parser.add_argument("--output", required=False, default="-", help="Output JSON path, or '-' for stdout")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repo_url: str = str(args.repo_url)
    limit: int = int(args.limit)
    output: str = str(args.output)

    spec = parse_repo_url(repo_url=repo_url)
    releases = fetch_releases(spec=spec, limit=limit)

    rows: list[dict[str, Any]] = []
    for release in releases:
        for asset in release.assets:
            is_binary: bool = looks_like_binary_asset(asset.name)
            os_name: str | None = classify_os(asset_name=asset.name)
            arch_name: str | None = classify_arch(asset_name=asset.name)
            rows.append({
                "tag": release.tag_name,
                "asset": asset.name,
                "binaryLike": is_binary,
                "os": os_name,
                "arch": arch_name,
            })

    payload: dict[str, Any] = {
        "repo": {"owner": spec.owner, "name": spec.repo},
        "releaseCount": len(releases),
        "rows": rows,
    }

    out_text: str = json.dumps(payload, indent=2, ensure_ascii=False)
    if output == "-":
        sys.stdout.write(out_text + "\n")
        return

    out_path = Path(output).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text + "\n", encoding="utf-8")
    sys.stdout.write(f"Wrote scan output to: {out_path}\n")


if __name__ == "__main__":
    main()
