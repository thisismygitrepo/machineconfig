

from pathlib import Path
from git import Repo


def add_ai_configs(repo_root: Path):
    import machineconfig as mc
    mc_root = Path(mc.__file__).parent

    try:
        _repo_obj = Repo(repo_root)
    except Exception as e:
        print(f"Error initializing git repo: {e}")
        return

    instructions_repository_dir = mc_root.joinpath("scripts/python/ai/instructions")
    chatmodes_dir = mc_root.joinpath("scripts/python/ai/chatmodes")
    prompts_dir = mc_root.joinpath("scripts/python/ai/prompts")
    python_rules_file = instructions_repository_dir.joinpath("python/dev.md")

    # VSCODE:
    # as per: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
    # Copilot Chat on github website chat & basic guideline.
    repo_root.joinpath(".github/chatmodes").mkdir(parents=True, exist_ok=True)
    repo_root.joinpath(".github/prompts").mkdir(parents=True, exist_ok=True)
    repo_root.joinpath(".github/instructions").mkdir(parents=True, exist_ok=True)
    for a_chatmode in chatmodes_dir.iterdir():
        repo_root.joinpath(".github/chatmodes", a_chatmode.stem + ".chatmode.md").write_text(data=a_chatmode.read_text(), encoding="utf-8")
    for a_prompt in prompts_dir.iterdir():
        repo_root.joinpath(".github/prompts", a_prompt.stem + ".prompt.md").write_text(data=a_prompt.read_text(), encoding="utf-8")
    for an_instruction in instructions_repository_dir.iterdir():
        repo_root.joinpath(".github/instructions", an_instruction.stem + ".instructions.md").write_text(data=an_instruction.read_text(), encoding="utf-8")
    tmp = repo_root.joinpath(".github/copilot-instructions.md")
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    # CURSOR, GEMINI, CLAUDE CODE.
    tmp = repo_root.joinpath(".cursor/rules/python_dev.mdc")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")
    tmp = repo_root.joinpath("CLAUDE.md")
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")
    tmp = repo_root.joinpath("GEMINI.md")
    tmp.write_text(data=python_rules_file.read_text(), encoding="utf-8")

    # OTHERS
    dot_ai_dir = repo_root.joinpath(".ai")
    dot_ai_dir.mkdir(parents=True, exist_ok=True)
    dot_git_ignore_path = repo_root.joinpath(".gitignore")
    if dot_git_ignore_path.exists():
        dot_git_ignore_content = dot_git_ignore_path.read_text(encoding="utf-8")
        to_add: list[str] = []
        to_check_for: list[str] = [".links", "notebooks", ".ai",
                                   "GEMINI.md", "CLAUDE.md", ".cursor", ".github"]
        for item in to_check_for:
            if item not in dot_git_ignore_content:
                to_add.append(item)
        # if "*.ipynb"
        if len(to_add) > 0:
            dot_git_ignore_path.write_text(data=dot_git_ignore_content + "\n" + "\n".join(to_add), encoding="utf-8")


if __name__ == "__main__":
    add_ai_configs(repo_root=Path.cwd())
