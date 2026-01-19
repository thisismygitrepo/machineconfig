
import argparse
import ast
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

type StringLocation = tuple[int, int, str]

type Resolution = tuple[Path | None, bool, str]


@dataclass(frozen=True)
class PathReference:
    source_file: Path
    line: int
    column: int
    raw: str
    resolved: Path | None
    exists: bool
    resolution: str


def iter_source_files(root: Path, extensions: set[str], exclude_dirs: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in exclude_dirs:
                continue
            continue
        if path.suffix.lower() in extensions:
            if any(part in exclude_dirs for part in path.parts):
                continue
            files.append(path)
    return files


def extract_strings_from_py(text: str) -> list[StringLocation]:
    results: list[StringLocation] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return results
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            line = getattr(node, "lineno", 1)
            col = getattr(node, "col_offset", 0)
            results.append((int(line), int(col), node.value))
    return results


def extract_strings_from_text(text: str) -> list[StringLocation]:
    results: list[StringLocation] = []
    pattern = re.compile(r"(['\"])(?P<val>(?:\\.|(?!\1).)*)\1")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in pattern.finditer(line):
            value = match.group("val")
            results.append((line_number, match.start(), value))
    return results


def is_path_like(value: str) -> bool:
    if value.strip() == "":
        return False
    if " " in value or "\t" in value or "\n" in value:
        return False
    if "://" in value:
        return False
    if value.startswith("$") or value.startswith("${") or value.startswith("%"):
        return False
    if value.startswith("./") or value.startswith("../") or value.startswith(".\\") or value.startswith("..\\"):
        return True
    if value.startswith("~/") or value.startswith("~\\"):
        return True
    if "/" in value or "\\" in value:
        return True
    if re.match(r"^[A-Za-z]:\\", value) is not None:
        return True
    return False


def resolve_reference(value: str, file_path: Path, repo_root: Path) -> Resolution:
    expanded = os.path.expandvars(value)
    candidates: list[tuple[str, Path]] = []
    raw_path = Path(expanded)
    if value.startswith("~"):
        candidates.append(("expanduser", Path(expanded).expanduser()))
    if raw_path.is_absolute():
        candidates.append(("absolute", raw_path))
    else:
        candidates.append(("relative_to_file", file_path.parent / expanded))
        candidates.append(("relative_to_repo", repo_root / expanded))
        candidates.append(("as_is", raw_path))
    for label, candidate in candidates:
        if candidate.exists():
            return candidate, True, label
    return (candidates[0][1] if candidates else None), False, (candidates[0][0] if candidates else "none")


def scan_file(file_path: Path, repo_root: Path) -> list[PathReference]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    if file_path.suffix.lower() == ".py":
        strings = extract_strings_from_py(text)
    else:
        strings = extract_strings_from_text(text)
    references: list[PathReference] = []
    for line, col, value in strings:
        if not is_path_like(value):
            continue
        resolved, exists, label = resolve_reference(value, file_path, repo_root)
        references.append(
            PathReference(
                source_file=file_path,
                line=line,
                column=col,
                raw=value,
                resolved=resolved,
                exists=exists,
                resolution=label,
            )
        )
    return references


def write_report(output_path: Path, root: Path, references: list[PathReference]) -> None:
    payload: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "total_files": len({ref.source_file for ref in references}),
        "total_references": len(references),
        "references": [
            {
                "source_file": str(ref.source_file),
                "line": ref.line,
                "column": ref.column,
                "raw": ref.raw,
                "resolved": str(ref.resolved) if ref.resolved is not None else None,
                "exists": ref.exists,
                "resolution": ref.resolution,
            }
            for ref in references
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(args: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parsed = parser.parse_args(args)
    root = Path(parsed.root).resolve()
    output_path = Path(parsed.output).resolve()
    extensions = {".sh", ".json", ".py", ".ps1"}
    exclude_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        "dist",
        "build",
    }
    files = iter_source_files(root, extensions, exclude_dirs)
    references: list[PathReference] = []
    for file_path in files:
        references.extend(scan_file(file_path, root))
    write_report(output_path, root, references)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
