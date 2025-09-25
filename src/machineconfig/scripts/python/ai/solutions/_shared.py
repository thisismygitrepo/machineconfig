from pathlib import Path
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

def get_generic_instructions_path() -> Path:
    return LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/instructions/python/dev.instructions.md")
