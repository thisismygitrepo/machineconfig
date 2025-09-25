from pathlib import Path

from machineconfig.scripts.python.ai.solutions._shared import get_generic_instructions_path
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    repo_root.joinpath("GEMINI.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")

    gemini_dir = repo_root.joinpath(".gemini")
    settings_source_path = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/gemini/settings.json")
    gemini_dir.mkdir(parents=True, exist_ok=True)

    settings_source_path.write_text(data=settings_source_path.read_text(encoding="utf-8"), encoding="utf-8")
