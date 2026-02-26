import json
from pathlib import Path
from typing import Any

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path
from machineconfig.scripts.python.helpers.helpers_agents.privacy.configs.opencode.opencode_privacy import (
    load_existing_config,
)


DEFAULT_OPENCODE_CONFIG: dict[str, Any] = {
    "$schema": "https://opencode.ai/config.json",
    "share": "disabled",
    "autoupdate": False,
    "instructions": ["AGENTS.md", ".github/instructions/*.md"],
    "permission": {
        "*": "ask",
        "external_directory": "ask",
        "edit": "ask",
        "task": "ask",
        "webfetch": "deny",
        "websearch": "deny",
        "codesearch": "deny",
        "bash": {"*": "ask", "git *": "allow"},
        "read": {
            "*": "allow",
            "*.env": "deny",
            "*.env.*": "deny",
            "*.env.example": "allow",
        },
    },
    "mcp": {
        "context7": {
            "type": "remote",
            "url": "https://mcp.context7.com/mcp",
            "enabled": False,
        },
        "mcp_everything": {
            "type": "local",
            "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
            "enabled": False,
        },
    },
}


def _merge_defaults(existing: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(existing)
    for key, default_value in defaults.items():
        current_value = merged.get(key)
        if key == "instructions":
            if isinstance(current_value, list):
                merged_instructions: list[str] = [value for value in current_value if isinstance(value, str)]
                for pattern in default_value:
                    if pattern not in merged_instructions:
                        merged_instructions.append(pattern)
                merged[key] = merged_instructions
            elif key not in merged:
                merged[key] = list(default_value)
            continue
        if isinstance(default_value, dict):
            if isinstance(current_value, dict):
                merged[key] = _merge_defaults(current_value, default_value)
            elif key not in merged:
                merged[key] = default_value
            continue
        if key not in merged:
            merged[key] = default_value
    return merged


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, ensure_ascii=True)
    path.write_text(f"{serialized}\n", encoding="utf-8")


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    if add_instructions:
        instructions_path = get_generic_instructions_path()
        instructions_text = instructions_path.read_text(encoding="utf-8")
        opencode_instructions_dir = repo_root.joinpath(".github/instructions")
        opencode_instructions_dir.mkdir(parents=True, exist_ok=True)
        opencode_rules_path = opencode_instructions_dir.joinpath("opencode_rules.md")
        opencode_rules_path.write_text(data=instructions_text, encoding="utf-8")
        agents_path = repo_root.joinpath("AGENTS.md")
        if agents_path.exists() is False:
            agents_path.write_text(data=instructions_text, encoding="utf-8")

    if add_private_config:
        opencode_config = repo_root.joinpath("opencode.json")
        existing_config = load_existing_config(opencode_config)
        merged_config = _merge_defaults(existing=existing_config, defaults=DEFAULT_OPENCODE_CONFIG)
        _write_json(path=opencode_config, payload=merged_config)
