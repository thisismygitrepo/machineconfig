from pathlib import Path
from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path

def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    if add_instructions:
        instructions_path = get_generic_instructions_path()
        opencode_instructions_dir = repo_root.joinpath(".github/instructions")
        opencode_instructions_dir.mkdir(parents=True, exist_ok=True)
        opencode_rules_path = opencode_instructions_dir.joinpath("opencode_rules.md")
        opencode_rules_path.write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")

    if add_private_config:
        opencode_config = repo_root.joinpath("opencode.json")
        if not opencode_config.exists():
            opencode_config.write_text('{\n  "$schema": "https://opencode.ai/config.json",\n  "instructions": [".github/instructions/*.md"]\n}', encoding="utf-8")
