from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    cline_dir = repo_root.joinpath(".clinerules")
    cline_dir.mkdir(parents=True, exist_ok=True)
    cline_dir.joinpath("python_dev.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
