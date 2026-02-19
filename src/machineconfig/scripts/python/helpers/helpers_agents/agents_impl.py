"""Pure Python implementations for agents commands - no typer dependencies."""

from typing import Optional, cast
from pathlib import Path


def agents_create(
    agent: str,
    host: str,
    model: str,
    provider: str,
    context_path: Optional[str],
    separator: str,
    agent_load: int,
    prompt: Optional[str],
    prompt_path: Optional[str],
    job_name: str,
    separate: bool,
    output_path: Optional[str],
    agents_dir: Optional[str],
) -> None:
    """Create agents layout file, ready to run."""
    from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_help_launch import prep_agent_launch, get_agents_launch_layout
    from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_load_balancer import chunk_prompts
    from machineconfig.utils.accessories import get_repo_root, randstr
    import json

    prompt_options = [prompt, prompt_path]
    provided_prompt = [opt for opt in prompt_options if opt is not None]
    if len(provided_prompt) != 1:
        raise ValueError("Exactly one of --prompt or --prompt-path must be provided")

    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        raise RuntimeError("💥 Could not determine the repository root. Please run this script from within a git repository.")

    print(f"Operating @ {repo_root}")

    if context_path is None:
        context_path_resolved = Path(repo_root) / ".ai" / "todo"
    else:
        context_path_resolved = Path(context_path).expanduser().resolve()

    if not context_path_resolved.exists():
        raise ValueError(f"Path does not exist: {context_path_resolved}")

    if context_path_resolved.is_file():
        prompt_material_re_splitted = chunk_prompts(context_path_resolved, tasks_per_prompt=agent_load, joiner=separator)
    elif context_path_resolved.is_dir():
        files = [f for f in context_path_resolved.rglob("*") if f.is_file()]
        if not files:
            raise ValueError(f"No files found in directory: {context_path_resolved}")
        concatenated = separator.join(f.read_text(encoding="utf-8") for f in files)
        prompt_material_re_splitted = [concatenated]
    else:
        raise ValueError(f"Path is neither file nor directory: {context_path_resolved}")

    if prompt_path is not None:
        prompt_prefix = Path(prompt_path).read_text(encoding="utf-8")
    else:
        prompt_prefix = cast(str, prompt)

    agent_selected = agent
    if agents_dir is None:
        agents_dir_obj = Path(repo_root) / ".ai" / f"tmp_prompts/{job_name}_{randstr()}"
    else:
        import shutil
        if Path(agents_dir).exists():
            shutil.rmtree(agents_dir)
        agents_dir_obj = Path(agents_dir)

    from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import HOST, AGENTS, PROVIDER
    prep_agent_launch(
        repo_root=repo_root,
        agents_dir=agents_dir_obj,
        prompts_material=prompt_material_re_splitted,
        keep_material_in_separate_file=separate,
        prompt_prefix=prompt_prefix,
        machine=cast(HOST, host),
        agent=cast(AGENTS, agent_selected),
        model=model,
        provider=cast(PROVIDER, provider),
        job_name=job_name,
    )
    layoutfile = get_agents_launch_layout(session_root=agents_dir_obj)

    layout_output_path = Path(output_path) if output_path is not None else agents_dir_obj / "layout.json"
    layout_output_path.parent.mkdir(parents=True, exist_ok=True)
    layout_output_path.write_text(data=json.dumps(layoutfile, indent=4), encoding="utf-8")
    print(f"Created agents in {agents_dir_obj}")
    print(f"Created layout in {layout_output_path}")


def collect(agent_dir: str, output_path: str, separator: str, pattern: Optional[str]) -> None:
    """Collect all material files from an agent directory and concatenate them."""
    if not Path(agent_dir).exists() or not Path(agent_dir).is_dir():
        raise ValueError(f"Agent directory does not exist or is not a directory: {agent_dir}")

    prompts_dir = Path(agent_dir) / "prompts"
    if not prompts_dir.exists():
        raise ValueError(f"Prompts directory not found: {prompts_dir}")

    material_files: list[Path] = []
    for agent_subdir in prompts_dir.iterdir():
        if pattern is None:
            if agent_subdir.is_dir() and agent_subdir.name.startswith("agent_"):
                material_file = agent_subdir / f"{agent_subdir.name}_material.txt"
                if material_file.exists():
                    material_files.append(material_file)
        else:
            if agent_subdir.is_dir():
                for material_file in agent_subdir.glob(pattern):
                    if material_file.is_file():
                        material_files.append(material_file)

    if not material_files:
        print("No material files found in the agent directory.")
        return
    print(f"Found {len(material_files)} material files. Concatenating...")
    for idx, a_file in enumerate(material_files):
        print(f"{idx+1}. {a_file}")
    material_files.sort(key=lambda x: int(x.parent.name.split("_")[-1]))
    concatenated_content: list[str] = []
    for material_file in material_files:
        content = material_file.read_text(encoding="utf-8")
        concatenated_content.append(content)
    result = separator.join(concatenated_content)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(result, encoding="utf-8")
    print(f"Concatenated material written to {output_path}")


def make_agents_command_template() -> None:
    """Create a template for fire agents."""
    from platform import system
    import machineconfig.scripts.python.helpers.helpers_agents as module

    if system() == "Linux" or system() == "Darwin":
        template_path = Path(module.__file__).parent / "templates/template.sh"
    elif system() == "Windows":
        template_path = Path(module.__file__).parent / "templates/template.ps1"
    else:
        raise ValueError(f"Unsupported OS: {system()}")

    from machineconfig.utils.accessories import get_repo_root
    repo_root = get_repo_root(Path.cwd())
    if repo_root is None:
        raise RuntimeError("💥 Could not determine the repository root. Please run this script from within a git repository.")

    save_path_root = repo_root / ".ai" / "agents"

    save_path_root.mkdir(parents=True, exist_ok=True)
    save_path_root.joinpath("template_fire_agents.sh").write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Template bash script written to {save_path_root}")

    from machineconfig.scripts.python.ai.utils.generate_files import make_todo_files
    make_todo_files(
        pattern=".py", repo=str(repo_root), strategy="name", output_path=str(save_path_root / "files.md"), split_every=None, split_to=None
    )

    prompt_path = Path(module.__file__).parent / "templates/prompt.txt"
    save_path_root.joinpath("prompt.txt").write_text(prompt_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Prompt template written to {save_path_root}")


def init_config(root: Optional[str], frameworks: tuple[str, ...], all_frameworks: bool, include_common: bool, add_lint_task: bool) -> None:
    """Initialize AI configurations in the current repository."""
    from machineconfig.scripts.python.ai.initai import DEFAULT_AI_FRAMEWORKS, add_ai_configs
    from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_helper_types import AI_FRAMEWORK

    if root is None:
        repo_root = Path.cwd()
    else:
        repo_root = Path(root).expanduser().resolve()

    if all_frameworks:
        selected_frameworks: tuple[AI_FRAMEWORK, ...] = DEFAULT_AI_FRAMEWORKS
    elif len(frameworks) > 0:
        selected_frameworks_list: list[AI_FRAMEWORK] = []
        for framework in frameworks:
            if framework not in DEFAULT_AI_FRAMEWORKS:
                raise ValueError(f"Unsupported framework: {framework}")
            selected_frameworks_list.append(framework)
        selected_frameworks = tuple(dict.fromkeys(selected_frameworks_list))
    else:
        raise ValueError("Provide at least one --framework option, or pass --all-frameworks")

    add_ai_configs(repo_root=repo_root, frameworks=selected_frameworks, include_common_scaffold=include_common, add_vscode_task=add_lint_task)
