EXECUTION_SCRIPT_TEMPLATE = r'''
import os
import json
import platform
import getpass
from pathlib import Path
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel

from machineconfig.utils.accessories import pprint
from machineconfig.utils.io import read_json
from machineconfig.cluster.remote.models import WorkloadParams, JOB_STATUS
from machineconfig.cluster.remote.job_params import JobParams
from machineconfig.cluster.remote.file_manager import FileManager

console = Console()

params: JobParams = JobParams.from_dict(read_json(Path(r"{params_json_path}").expanduser()))
manager: FileManager = FileManager.from_json_file(r"{file_manager_json_path}")

print("\n" + "=" * 80)
manager.secure_resources()
pid: int = os.getpid()
log_dir = manager.execution_log_dir.expanduser()
log_dir.mkdir(parents=True, exist_ok=True)
(log_dir / "pid.txt").write_text(str(pid), encoding="utf-8")
(log_dir / "status.txt").write_text("running", encoding="utf-8")

time_start_utc = datetime.now(timezone.utc)
time_start_local = datetime.now()
(log_dir / "start_time.txt").write_text(str(time_start_local), encoding="utf-8")
func_kwargs: dict = read_json(manager.kwargs_path.expanduser())

print("\n" + "=" * 80)
console.rule(title="EXECUTION START", style="bold red", characters="=")
console.print(f"File: {{params.file_path_rh}}\nFunction: {{params.func_name}}\nTime: {{time_start_local}}", style="bold blue")
if isinstance(func_kwargs, dict):
    pprint(func_kwargs, "Function Arguments")

res = None
error_message = ""

{execution_line}

print("\n" + "=" * 80)
console.rule(title="EXECUTION END", style="bold green", characters="=")

if isinstance(res, (str, Path)) and Path(res).expanduser().exists():
    res_folder = Path(res).expanduser()
else:
    res_folder = Path.home() / f"tmp_results/tmp_dirs/{{manager.job_id}}"
    res_folder.mkdir(parents=True, exist_ok=True)
    console.print(Panel(f"Function did not return a results path. Using: {{res_folder}}", title="Result Directory", border_style="yellow"))

time_end_utc = datetime.now(timezone.utc)
time_end_local = datetime.now()
delta = time_end_utc - time_start_utc

(log_dir / "end_time.txt").write_text(str(time_end_local), encoding="utf-8")
(log_dir / "results_folder_path.txt").write_text(str(res_folder), encoding="utf-8")
(log_dir / "error_message.txt").write_text(error_message or params.error_message, encoding="utf-8")

job_status: str
if not params.error_message:
    job_status = "completed"
    print(f"JOB COMPLETED | id={{manager.job_id}} | duration={{delta}} | results={{res_folder}}")
else:
    job_status = "failed"
    print(f"JOB FAILED | id={{manager.job_id}} | duration={{delta}} | error={{params.error_message}}")
(log_dir / "status.txt").write_text(job_status, encoding="utf-8")

exec_times = {{"start_utc": str(time_start_utc), "end_utc": str(time_end_utc), "start_local": str(time_start_local), "end_local": str(time_end_local), "delta": str(delta), "submission_time": str(manager.submission_time), "wait_time": str(time_start_local - manager.submission_time)}}
pprint(exec_times, "Execution Times")

ssh_repr_remote = params.ssh_repr_remote or f"{{getpass.getuser()}}@{{platform.node()}}"
console.print(Panel(f"ftprx {{ssh_repr_remote}} {{res_folder}} -r", title="Pull results:", border_style="bold red"))

{notification_block}

manager.unlock_resources()

console.rule(title="END OF EXECUTION SCRIPT", style="bold green", characters="=")
'''


def render_execution_script(params_json_path: str, file_manager_json_path: str, execution_line: str, notification_block: str) -> str:
    return EXECUTION_SCRIPT_TEMPLATE.format(
        params_json_path=params_json_path,
        file_manager_json_path=file_manager_json_path,
        execution_line=execution_line,
        notification_block=notification_block,
    )
