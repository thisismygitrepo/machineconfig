from pathlib import Path

from machineconfig.scripts.python.ai.solutions._shared import get_generic_instructions_path


def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    repo_root.joinpath("GEMINI.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
    settings_source_path = Path("./settings.json")
    gemini_dir = repo_root.joinpath(".gemini")
    gemini_dir.mkdir(parents=True, exist_ok=True)
    gemini_dir.joinpath("settings.json").write_text(data=settings_source_path.read_text(encoding="utf-8"), encoding="utf-8")
