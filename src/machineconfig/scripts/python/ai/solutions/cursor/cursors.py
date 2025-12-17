from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    cursor_rules_path = repo_root.joinpath(".cursor/rules/python_dev.mdc")
    cursor_rules_path.parent.mkdir(parents=True, exist_ok=True)
    cursor_rules_path.write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
