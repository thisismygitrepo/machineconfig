from pathlib import Path
from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path


def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    _ = add_private_config
    if add_instructions is False:
        return
    instructions_path = get_generic_instructions_path()

    warp_md = repo_root.joinpath("WARP.md")
    warp_md.write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
