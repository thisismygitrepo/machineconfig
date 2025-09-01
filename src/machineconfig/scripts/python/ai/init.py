

from pathlib import Path
from git import Repo

# def add_config_for_curor(repo_root: Path, config_f):

def add_ai_configs(repo_root: Path):
    import machineconfig as mc
    mc_root = Path(mc.__file__).parent

    try:
        _repo_obj = Repo(repo_root)
    except Exception as e:
        print(f"Error initializing git repo: {e}")
        return

    rules_dir = mc_root.joinpath("scripts/python/ai/rules")

    python_rules_file = rules_dir.joinpath("python/dev.md")

    tmp = repo_root.joinpath(".cursor/rules/python_dev.mdc")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    # as per: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
    # Copilot Chat on github website chat
    tmp = repo_root.joinpath(".github/copilot-instructions.md")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    tmp = repo_root.joinpath(".github/instructions/python01.instructions.md")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    tmp = repo_root.joinpath("CLAUDE.md")
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")
    tmp = repo_root.joinpath("GEMINI.md")
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    dot_ai_dir = repo_root.joinpath(".ai")
    dot_ai_dir.mkdir(parents=True, exist_ok=True)
    dot_git_ignore_path = dot_ai_dir.joinpath(".gitignore")
    if dot_git_ignore_path.exists():
        dot_git_ignore_content = dot_git_ignore_path.read_text(encoding="utf-8")
        to_add: list[str] = []
        if ".links" not in dot_git_ignore_content: to_add.append(".links")
        if "notebooks" not in dot_git_ignore_content: to_add.append("notebooks")
        if ".ai" not in dot_git_ignore_content: to_add.append(".ai")
        # if "*.ipynb"
        if len(to_add) > 0:
            dot_git_ignore_path.write_text(data=dot_git_ignore_content + "\n" + "\n".join(to_add), encoding="utf-8")


if __name__ == "__main__":
    add_ai_configs(repo_root=Path.cwd())
