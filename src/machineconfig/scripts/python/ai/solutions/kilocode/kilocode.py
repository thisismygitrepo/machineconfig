from pathlib import Path
from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    _ = add_private_config
    if add_instructions is False:
        return
    instructions_path = get_generic_instructions_path()

    kilo_rules_dir = repo_root.joinpath(".kilocode/rules")
    kilo_rules_dir.mkdir(parents=True, exist_ok=True)

    rules_path = kilo_rules_dir.joinpath("rules.md")
    rules_path.write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
