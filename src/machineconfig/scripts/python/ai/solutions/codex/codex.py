from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    codex_dir = repo_root.joinpath(".codex")
    codex_dir.mkdir(parents=True, exist_ok=True)
    codex_dir.joinpath("AGENTS.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
