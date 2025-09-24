

from typing import Literal, TypeAlias
from math import ceil


SPLITTING_STRATEGY: TypeAlias = Literal[
    "agent_cap",  # User decides number of agents, rows/tasks determined automatically
    "task_rows"   # User decides number of rows/tasks, number of agents determined automatically
]
DEFAULT_AGENT_CAP = 6


def chunk_prompts(prompts: list[str], strategy: SPLITTING_STRATEGY, joiner: str, *, agent_cap: int | None, task_rows: int | None) -> list[str]:
    """Chunk prompts based on splitting strategy.
    
    Args:
        prompts: List of prompts to chunk
        strategy: Either 'agent_cap' or 'task_rows'  
        agent_cap: Maximum number of agents (used with 'agent_cap' strategy)
        task_rows: Number of rows/tasks per agent (used with 'task_rows' strategy)
    """
    prompts = [p for p in prompts if p.strip() != ""]  # drop blank entries
    
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

def redistribute_prompts(prompt_material: str, separator: str, splitting_strategy: SPLITTING_STRATEGY) -> list[str]:

    prompt_material_splitted = prompt_material.split(separator)
    print(f"Loaded {len(prompt_material_splitted)} raw prompts from source.")
    # Prompt user for splitting strategy
    # Get parameters based on strategy
    if splitting_strategy == "agent_cap":
        agent_cap_input = input(f"Enter maximum number of agents/splits [default: {DEFAULT_AGENT_CAP}]: ").strip()
        agent_cap = int(agent_cap_input) if agent_cap_input else DEFAULT_AGENT_CAP
        prompt_material_re_splitted = chunk_prompts(prompt_material_splitted, splitting_strategy, agent_cap=agent_cap, task_rows=None, joiner=separator)
        max_agents_for_launch = agent_cap
    elif splitting_strategy == "task_rows":
        task_rows_input = input("Enter number of rows/tasks per agent [13]: ").strip() or "13"
        task_rows = int(task_rows_input)
        prompt_material_re_splitted = chunk_prompts(prompt_material_splitted, splitting_strategy, agent_cap=None, task_rows=task_rows, joiner=separator)
        max_agents_for_launch = len(prompt_material_re_splitted)  # Number of agents determined by chunking
    else:
        raise ValueError(f"Unknown splitting strategy: {splitting_strategy}")
    _ = max_agents_for_launch  # to be used later
    return prompt_material_re_splitted
