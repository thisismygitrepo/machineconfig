from typing import Literal, TypeAlias
from math import ceil
from pathlib import Path


SPLITTING_STRATEGY: TypeAlias = Literal[
    "agent_cap",  # User decides number of agents, rows/tasks determined automatically
    "task_rows",  # User decides number of rows/tasks, number of agents determined automatically
]
DEFAULT_AGENT_CAP = 6


def chunk_prompts(prompt_material_path: Path, strategy: SPLITTING_STRATEGY, joiner: str, *, agent_cap: int | None, task_rows: int | None) -> list[str]:
    """Chunk prompts based on splitting strategy.

    Args:
        prompts: List of prompts to chunk
        strategy: Either 'agent_cap' or 'task_rows'
        agent_cap: Maximum number of agents (used with 'agent_cap' strategy)
        task_rows: Number of rows/tasks per agent (used with 'task_rows' strategy)
    """
    prompts = [p for p in prompt_material_path.read_text(encoding="utf-8", errors="ignore").split(joiner) if p.strip() != ""]  # drop blank entries

    if strategy == "agent_cap":
        if agent_cap is None:
            raise ValueError("agent_cap must be provided when using 'agent_cap' strategy")

        if len(prompts) <= agent_cap:
            return prompts

        print(f"Chunking {len(prompts)} prompts into groups for up to {agent_cap} agents because it exceeds the cap.")
        chunk_size = ceil(len(prompts) / agent_cap)
        grouped: list[str] = []
        for i in range(0, len(prompts), chunk_size):
            grouped.append(joiner.join(prompts[i : i + chunk_size]))
        return grouped

    elif strategy == "task_rows":
        if task_rows is None:
            raise ValueError("task_rows must be provided when using 'task_rows' strategy")
        if task_rows >= len(prompts):
            return prompts
        print(f"Chunking {len(prompts)} prompts into groups of {task_rows} rows/tasks each.")
        grouped: list[str] = []
        for i in range(0, len(prompts), task_rows):
            grouped.append(joiner.join(prompts[i : i + task_rows]))
        return grouped

    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")
