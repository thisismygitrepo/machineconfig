import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_URL = "https://opencode.ai/config.json"

PRIVACY_PERMISSION: dict[str, Any] = {
    "*": "ask",
    "webfetch": "deny",
    "external_directory": "ask",
    "bash": {"*": "ask", "git *": "allow"},
    "edit": "ask",
    "read": {
        "*": "allow",
        "*.env": "deny",
        "*.env.*": "deny",
        "*.env.example": "allow",
    },
}

PRIVACY_CONFIG: dict[str, Any] = {
    "$schema": SCHEMA_URL,
    "share": "disabled",
    "autoupdate": False,
    "permission": PRIVACY_PERMISSION,
    "enabled_providers": ["local"],
}


def strip_jsonc(text: str) -> str:
    result: list[str] = []
    in_string = False
    string_char = ""
    in_line_comment = False
    in_block_comment = False
    index = 0

    while index < len(text):
        ch = text[index]
        next_ch = text[index + 1] if index + 1 < len(text) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                result.append(ch)
            index += 1
            continue

        if in_block_comment:
            if ch == "*" and next_ch == "/":
                in_block_comment = False
                index += 2
            else:
                index += 1
            continue

        if in_string:
            result.append(ch)
            if ch == "\\":
                if index + 1 < len(text):
                    result.append(text[index + 1])
                    index += 2
                    continue
            elif ch == string_char:
                in_string = False
            index += 1
            continue

        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            result.append(ch)
            index += 1
            continue

        if ch == "/" and next_ch == "/":
            in_line_comment = True
            index += 2
            continue

        if ch == "/" and next_ch == "*":
            in_block_comment = True
            index += 2
            continue

        result.append(ch)
        index += 1

    return "".join(result)


def load_existing_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    raw_text = path.read_text(encoding="utf-8")
    stripped_text = strip_jsonc(raw_text)
    try:
        parsed = json.loads(stripped_text)
    except json.JSONDecodeError as exc:
        message = f"Failed to parse existing config at {path}: {exc}"
        raise ValueError(message) from exc

    if not isinstance(parsed, dict):
        message = f"Expected JSON object in {path}, found {type(parsed).__name__}"
        raise ValueError(message)

    return parsed


def apply_privacy_config(existing: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in PRIVACY_CONFIG.items():
        merged[key] = value
    if "$schema" not in merged:
        merged["$schema"] = SCHEMA_URL
    return merged


def resolve_repo_root(repo_path_value: str | None) -> Path:
    if repo_path_value is not None:
        return Path(repo_path_value).expanduser().resolve()

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = "Unable to detect git repo root. Provide --repo-path for repo scope."
        raise ValueError(message)
    return Path(result.stdout.strip()).resolve()


def write_config(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(config, indent=2, ensure_ascii=True)
    path.write_text(f"{serialized}\n", encoding="utf-8")


def apply_opencode_privacy(scope: str, repo_path: str | None = None) -> None:
    try:
        if scope == "global":
            config_path = Path.home() / ".config" / "opencode" / "opencode.json"
        else:
            repo_root = resolve_repo_root(repo_path)
            config_path = repo_root / "opencode.json"

        existing_config = load_existing_config(config_path)
        updated_config = apply_privacy_config(existing_config)
        write_config(config_path, updated_config)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return

    print(f"Wrote OpenCode config to {config_path}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Apply privacy-first OpenCode config.")
    parser.add_argument("--scope", choices=["global", "repo"], required=True)
    parser.add_argument("--repo-path")
    args = parser.parse_args(argv)

    scope_value = args.scope
    repo_path_value = args.repo_path

    apply_opencode_privacy(scope_value, repo_path_value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
