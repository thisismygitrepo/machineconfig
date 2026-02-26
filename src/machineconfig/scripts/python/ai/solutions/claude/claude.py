import json
from pathlib import Path

from machineconfig.scripts.python.ai.utils import generic
from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path

SETTINGS_SCHEMA_URL = "https://json.schemastore.org/claude-code-settings.json"


def _write_json_if_missing(path: Path, content: dict[str, object]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data=json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _shared_project_settings() -> dict[str, object]:
    return {
        "$schema": SETTINGS_SCHEMA_URL,
        "respectGitignore": True,
        "permissions": {
            "deny": [
                "Read(./.env)",
                "Read(./.env.*)",
                "Read(./secrets/**)",
                "Read(./config/credentials.json)",
                "Bash(curl *)",
                "Bash(wget *)",
            ]
        },
        "enableAllProjectMcpServers": False,
    }


def _private_local_settings() -> dict[str, object]:
    return {
        "$schema": SETTINGS_SCHEMA_URL,
        "env": {
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1",
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
            "DISABLE_BUG_COMMAND": "1",
        },
    }


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    if add_instructions:
        instructions_path = get_generic_instructions_path()
        repo_root.joinpath("CLAUDE.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")

    if add_private_config:
        _write_json_if_missing(path=repo_root.joinpath(".claude/settings.json"), content=_shared_project_settings())
        _write_json_if_missing(path=repo_root.joinpath(".claude/settings.local.json"), content=_private_local_settings())
        _write_json_if_missing(path=repo_root.joinpath(".mcp.json"), content={"mcpServers": {}})

        claude_local_path = repo_root.joinpath("CLAUDE.local.md")
        if claude_local_path.exists() is False:
            claude_local_path.write_text(
                data=(
                    "# Local Claude Code preferences\n\n"
                    "- Keep credentials in environment variables, never in tracked files.\n"
                    "- Store personal workflow notes here; do not commit sensitive context.\n"
                    "- Use `.mcp.json` for shared MCP servers and keep secrets in local environment variables.\n"
                ),
                encoding="utf-8",
            )

        dot_git_ignore_path = repo_root.joinpath(".gitignore")
        if dot_git_ignore_path.exists() is False:
            dot_git_ignore_path.touch()
        generic.adjust_gitignore(
            repo_root=repo_root,
            include_default_entries=False,
            extra_entries=[".claude/settings.local.json", "CLAUDE.local.md"],
        )
