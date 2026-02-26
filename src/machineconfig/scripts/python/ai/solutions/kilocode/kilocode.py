import json
from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def _write_json_if_missing(path: Path, content: dict[str, object]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data=json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _write_text_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data=content, encoding="utf-8")


def _default_kilocodeignore() -> str:
    return (
        "# Secrets and credentials\n"
        ".env\n"
        ".env.*\n"
        "secrets/\n"
        "**/*.pem\n"
        "**/*.key\n"
        "**/credentials*.json\n"
        "!*.env.example\n"
    )


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    kilo_rules_dir = repo_root.joinpath(".kilocode/rules")

    if add_instructions:
        instructions_text = get_generic_instructions_path().read_text(encoding="utf-8")
        kilo_rules_dir.mkdir(parents=True, exist_ok=True)
        kilo_rules_dir.joinpath("rules.md").write_text(data=instructions_text, encoding="utf-8")
        _write_text_if_missing(path=repo_root.joinpath("AGENTS.md"), content=instructions_text)

    if add_private_config:
        _write_json_if_missing(path=repo_root.joinpath(".kilocode/mcp.json"), content={"mcpServers": {}})
        _write_text_if_missing(path=repo_root.joinpath(".kilocodeignore"), content=_default_kilocodeignore())
        privacy_source = Path(__file__).with_name("privacy.md")
        _write_text_if_missing(path=kilo_rules_dir.joinpath("privacy.md"), content=privacy_source.read_text(encoding="utf-8"))
