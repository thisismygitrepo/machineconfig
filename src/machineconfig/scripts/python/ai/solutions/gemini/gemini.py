from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    if add_instructions:
        instructions_path = get_generic_instructions_path()
        repo_root.joinpath("GEMINI.md").write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")

    if add_private_config:
        gemini_dir = repo_root.joinpath(".gemini")
        settings_source_path = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/gemini/settings.json")
        gemini_dir.mkdir(parents=True, exist_ok=True)
        gemini_dir.joinpath("settings.json").write_text(data=settings_source_path.read_text(encoding="utf-8"), encoding="utf-8")
