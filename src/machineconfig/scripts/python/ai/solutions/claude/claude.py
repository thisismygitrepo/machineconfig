from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    repo_root.joinpath("CLAUDE.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
