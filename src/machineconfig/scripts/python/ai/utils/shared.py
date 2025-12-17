from pathlib import Path
from machineconfig.utils.source_of_truth import LIBRARY_ROOT

def get_generic_instructions_path() -> Path:
    path = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/instructions/python/dev.instructions.md")
    text = path.read_text(encoding="utf-8")
    import platform
    if platform.system().lower() == "windows":
        text = text.replace("bash", "powershell").replace(".sh", ".ps1")
    import tempfile
    temp_path = Path(tempfile.gettempdir()).joinpath("generic_instructions.md")
    temp_path.write_text(data=text, encoding="utf-8")
    return temp_path
