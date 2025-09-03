

from pathlib import Path


installations = """
uv add pylint pyright mypy pyrefly ty --dev  # linters and type checkers
uv add pytest --dev
"""

def add_ai_configs(repo_root: Path):
    import machineconfig as mc
    mc_root = Path(mc.__file__).parent
    # from git import Repo
    # try:
    #     _repo_obj = Repo(repo_root)
    # except Exception as _e:
    #     print(f"{Path.cwd()} is not a git repository, would you like to initialize one? (y/n)")
    #     if input().strip().lower() == "y":
    #         Repo.init(repo_root)
    #     return
    if repo_root.joinpath("pyproject.toml").exists() is False:
        uv_init = input(f"{repo_root} does not seem to be a python project (no pyproject.toml found), would you like to initialize one? (y/n) ")
        if uv_init.strip().lower() == "y":
            command_to_run = """
uv init --python 3.13
uv venv
"""
            import subprocess
            subprocess.run(command_to_run, shell=True, check=True)
        else:
            print("Terminating mcinit ...")
            return

    instructions_repository_dir = mc_root.joinpath("scripts/python/ai/instructions")
    chatmodes_dir = mc_root.joinpath("scripts/python/ai/chatmodes")
    prompts_dir = mc_root.joinpath("scripts/python/ai/prompts")
    # python_rules_file = instructions_repository_dir.joinpath("python/dev.md")

    # VSCODE:
    # as per: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
    # Copilot Chat on github website chat & basic guideline.
    repo_root.joinpath(".github/chatmodes").mkdir(parents=True, exist_ok=True)
    repo_root.joinpath(".github/prompts").mkdir(parents=True, exist_ok=True)
    repo_root.joinpath(".github/instructions").mkdir(parents=True, exist_ok=True)
    for a_chatmode in chatmodes_dir.iterdir():
        repo_root.joinpath(".github/chatmodes", a_chatmode.name.split(".")[0] + ".chatmode.md").write_text(data=a_chatmode.read_text(encoding="utf-8"), encoding="utf-8")
    for a_prompt in prompts_dir.iterdir():
        repo_root.joinpath(".github/prompts", a_prompt.name.split(".")[0] + ".prompt.md").write_text(data=a_prompt.read_text(encoding="utf-8"), encoding="utf-8")
    for an_instruction in instructions_repository_dir.rglob("*.md"):
        repo_root.joinpath(".github/instructions", an_instruction.name.split(".")[0] + ".instruction.md").write_text(data=an_instruction.read_text(encoding="utf-8"), encoding="utf-8")
    tmp = repo_root.joinpath(".github/copilot-instructions.md")

    generic_instructions = instructions_repository_dir.joinpath("python/dev.instructions.md")
    tmp.write_text(data=generic_instructions.read_text(encoding="utf-8"), encoding="utf-8")

    # CURSOR, GEMINI, CLAUDE CODE.
    tmp = repo_root.joinpath(".cursor/rules/python_dev.mdc")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(data=generic_instructions.read_text(encoding="utf-8"), encoding="utf-8")
    tmp = repo_root.joinpath("CLAUDE.md")
    tmp.write_text(data=generic_instructions.read_text(encoding="utf-8"), encoding="utf-8")

    tmp = repo_root.joinpath("GEMINI.md")
    tmp.write_text(data=generic_instructions.read_text(encoding="utf-8"), encoding="utf-8")
    gemini_settings = mc_root.joinpath("scripts/python/ai/configs/.gemini/settings.json")
    repo_root.joinpath(".gemini").mkdir(parents=True, exist_ok=True)
    repo_root.joinpath(".gemini/settings.json").write_text(data=gemini_settings.read_text(encoding="utf-8"), encoding="utf-8")

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
