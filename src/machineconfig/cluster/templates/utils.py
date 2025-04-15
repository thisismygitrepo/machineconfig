
"""
This module contains utility functions for the cluster module.
"""

import inspect
from crocodile.core import Save
from crocodile.file_management import P
from machineconfig.cluster.remote_machine import WorkloadParams
from typing import Optional, Any, Callable


def expensive_function(workload_params: WorkloadParams, sim_dict: Optional[dict[str, Any]] = None) -> P:
    import time
    from rich.progress import track
    print("Hello, I am one thread of an expensive function, and I just started running ...")
    print(f"Oh, I recieved this parameter: {sim_dict=} & {workload_params=} ")
    execution_time_in_seconds = 60 * 1
    steps = 100
    for _ in track(range(steps), description="Progress bar ..."):
        time.sleep(execution_time_in_seconds / steps)  # Simulate work being done
    print(f"I'm done, I crunched numbers from {workload_params.idx_start} to {workload_params.idx_end}.")
    _ = workload_params.idx_max

    save_dir = P.tmp().joinpath("tmp_dirs/expensive_function_single_thread").joinpath(workload_params.save_suffix, f"thread_{workload_params.idx_start}_{workload_params.idx_end}").create()
    Save.pickle(obj={'a': 1}, path=save_dir.joinpath("trial_func_result.pkl"))
    return save_dir


def assert_has_workload_params(func_or_method: Callable[..., Any]):
    if not inspect.isfunction(func_or_method) and not inspect.ismethod(func_or_method): raise TypeError(f"{func_or_method} is not a function or method.")
    try: params = inspect.signature(func_or_method).parameters
    except ValueError as e: raise ValueError(f"Failed to inspect signature of {func_or_method}: {e}") from e
    if 'workload_params' not in params: raise ValueError(f"{func_or_method.__name__}() does not have 'workload_params' parameter.")
    if params['workload_params'].kind != inspect.Parameter.POSITIONAL_OR_KEYWORD: raise ValueError(f"{func_or_method.__name__}() 'workload_params' parameter is not a positional or keyword parameter.")
    if params['workload_params'].default is not inspect.Parameter.empty: raise ValueError(f"{func_or_method.__name__}() 'workload_params' parameter should not have a default value.")
    return True
