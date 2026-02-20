from pathlib import Path
import json

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()

    codex_dir = repo_root.joinpath(".codex")
    codex_dir.mkdir(parents=True, exist_ok=True)

    config_toml = codex_dir.joinpath("config.toml")
    instructions = instructions_path.read_text(encoding="utf-8")
    escaped_instructions = json.dumps(instructions)
    toml_content = f"[instructions]\ncustom_rules = {escaped_instructions}\n"
    config_toml.write_text(data=toml_content, encoding="utf-8")
