from pathlib import Path

from machineconfig.scripts.python.ai.utils.shared import get_generic_instructions_path
from machineconfig.utils.source_of_truth import LIBRARY_ROOT



def build_configuration(repo_root: Path, add_private_config: bool, add_instructions: bool) -> None:
    instructions_repository_dir = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/instructions")
    agents_dir = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/agents")
    prompts_dir = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/prompts")
    privacy_path = LIBRARY_ROOT.joinpath("scripts/python/ai/solutions/copilot/privacy.md")

    github_dir = repo_root.joinpath(".github")
    agents_target_dir = github_dir.joinpath("agents")
    prompts_target_dir = github_dir.joinpath("prompts")
    instructions_target_dir = github_dir.joinpath("instructions")

    if add_private_config:
        agents_target_dir.mkdir(parents=True, exist_ok=True)
        prompts_target_dir.mkdir(parents=True, exist_ok=True)

        for agent_profile in sorted(agents_dir.iterdir()):
            if agent_profile.is_file() is False:
                continue
            if agent_profile.name.endswith(".agent.md"):
                target_name = agent_profile.name
            else:
                target_name = f"{agent_profile.name.split('.')[0]}.agent.md"
            agent_target = agents_target_dir.joinpath(target_name)
            agent_target.write_text(data=agent_profile.read_text(encoding="utf-8"), encoding="utf-8")

        for prompt in sorted(prompts_dir.iterdir()):
            if prompt.is_file() is False:
                continue
            if prompt.name.endswith(".prompt.md"):
                target_name = prompt.name
            else:
                target_name = f"{prompt.name.split('.')[0]}.prompt.md"
            prompt_target = prompts_target_dir.joinpath(target_name)
            prompt_target.write_text(data=prompt.read_text(encoding="utf-8"), encoding="utf-8")

    if add_instructions:
        instructions_target_dir.mkdir(parents=True, exist_ok=True)
        for instruction in sorted(instructions_repository_dir.rglob("*.md")):
            if instruction.name.endswith(".instructions.md"):
                target_name = instruction.name
            else:
                target_name = f"{instruction.name.split('.')[0]}.instructions.md"
            instruction_target = instructions_target_dir.joinpath(target_name)
            instruction_target.write_text(data=instruction.read_text(encoding="utf-8"), encoding="utf-8")

        privacy_instructions_target = instructions_target_dir.joinpath("copilot-cli-security.instructions.md")
        privacy_instructions_target.write_text(data=privacy_path.read_text(encoding="utf-8"), encoding="utf-8")

        generic_instructions_path = get_generic_instructions_path()
        github_dir.joinpath("copilot-instructions.md").write_text(data=generic_instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
