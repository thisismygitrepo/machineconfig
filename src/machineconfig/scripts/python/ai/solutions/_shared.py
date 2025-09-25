from pathlib import Path
from machineconfig.utils.source_of_truth import REPO_ROOT

def get_generic_instructions_path() -> Path:
    return REPO_ROOT.joinpath("scripts/python/ai/instructions/python/dev.instructions.md")
