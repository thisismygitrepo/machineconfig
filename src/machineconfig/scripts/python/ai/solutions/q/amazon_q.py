from pathlib import Path
from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path

def build_configuration(repo_root: Path) -> None:
    instructions_path = get_generic_instructions_path()
    
    amazon_q_rules_dir = repo_root.joinpath(".amazonq/rules")
    amazon_q_rules_dir.mkdir(parents=True, exist_ok=True)
    
    rules_path = amazon_q_rules_dir.joinpath("default_rules.md")
    rules_path.write_text(data=instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
