

"""Task scheduler
"""

from crocodile.file_management import P, Read, str2timedelta, Save
# from crocodile.meta import Terminal
from machineconfig.utils.utils import get_shell_script_executing_python_file
from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import subprocess
from typing import Optional
# from crocodile.meta import Scheduler


SCHEDULER_DEFAULT_ROOT = P.home().joinpath("dotfiles/scripts/.scheduler")
SUCCESS = "success"
DEFAULT_CONFIG = """
[specs]
frequency = 30d
start = 2024-01-01 01:00

[runtime]
venv = ve
"""


class Register:
    def __init__(self, root: str):
        self.root = P(root).expanduser().absolute()

    def register_runtime(self, frequency_months: int = 1):
        start, end = self.get_report_start_end_datetimes(frequency_months=frequency_months)
        report = Report(name="runtime", start=start, end=end, status="success")
        report.to_path(self.root.joinpath("runtime.ini"))
        return report

    def read_runtime(self):
        return Report.from_path(self.root.joinpath("runtime.ini"))

    @staticmethod
    def format_date(date: datetime):
        return str(date.year)[2:] + "-" + str(date.month).zfill(2)
    @staticmethod
    def get_report_start_end_datetimes(frequency_months: int):
        now = datetime.now()
        import numpy as np
        chunks = np.arange(start=1, stop=12, step=frequency_months)
        chunk_now_start_month: int = chunks[chunks <= now.month][-1]
        chunk_now_start = datetime(year=now.year, month=chunk_now_start_month, day=1)
        from dateutil.relativedelta import relativedelta
        previous_chunk_start = chunk_now_start - relativedelta(months=frequency_months)
        return previous_chunk_start, chunk_now_start


@dataclass
class Report:
    name: str
    start: datetime
    end: datetime
    status: str

    @classmethod
    def from_path(cls, path: P, return_default_if_not_found: bool = False):
        if not path.exists():
            if return_default_if_not_found:
                return Report(name=path.parent.name, start=datetime(year=2000, month=1, day=1), end=datetime(year=2000, month=1, day=1), status="NA")
            else:
                raise ValueError(f"Could not find report at {path}")
        ini = Read.ini(path)['report']
        return cls(
            name=ini["name"],
            start=datetime.fromisoformat(ini["start"]),
            end=datetime.fromisoformat(ini["end"]),
            status=ini["status"],
        )
    def to_path(self, path: P):
        Save.ini(path=path, obj={'report': {
            'name': self.name,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'status': str(self.status),
        }})


@dataclass
class Task:
    name: str
    task_root: P
    frequency: timedelta
    start: datetime
    venv: str
    @property
    def report_path(self):
        return self.task_root.joinpath("report.ini")


def read_task_from_dir(path: P):
    tasks_config = Read.ini(path.joinpath("config.ini"))
    task = Task(name=path.name,
                task_root=path,
                frequency=str2timedelta(tasks_config["specs"]["frequency"]),
                start=datetime.fromisoformat(tasks_config["specs"]["start"]),
                venv=tasks_config["runtime"]["venv"],
                # output_dir=P(a_task_section["output_dir"]).expanduser().absolute(),
                )
    return task


def main(root: Optional[str] = None, ignore_conditions: bool = True):
    if root is None: root_resolved = SCHEDULER_DEFAULT_ROOT
    else: root_resolved = P(root).expanduser().absolute()
    tasks_dirs = root_resolved.search(files=False, folders=True).filter(lambda x: x.joinpath("task.py").exists())

    print(root_resolved)
    tasks: list[Task] = []
    for a_dir in tasks_dirs:
        tasks.append(read_task_from_dir(a_dir))

    from machineconfig.utils.utils import choose_multiple_options
    import pandas as pd
    df_res = pd.DataFrame([Report.from_path(path=a_task.report_path).__dict__ for a_task in tasks])
    tasks_chosen_raw = choose_multiple_options(df_res.to_markdown().splitlines(), "Choose tasks to run")
    tasks_chosen = [tasks[int(a_task_chosen.split("|")[1])] for a_task_chosen in tasks_chosen_raw]

    result: list[Report] = []
    for a_task in tasks_chosen:
        if not ignore_conditions:
            answer, report = should_task_run(a_task)
        else:
            answer, report = True, None
        if answer: report = run_task(a_task)
        else:
            assert report is not None
        result.append(report)

    df_res = pd.DataFrame([r.__dict__ for r in result])
    print(df_res)
    # root_resolved.joinpath("task_report.md").write_text(df_res.to_markdown(), encoding="utf-8")
    return ""


def should_task_run(task: Task, tolerance_mins: int = 1440) -> tuple[bool, Optional[Report]]:
    if not task.report_path.exists():
        print(f"Task {task.name} has no record of being run before, running now...")
        return True, None
    old_report = Report.from_path(task.report_path)
    time_since_execution = datetime.now() - old_report.end
    if time_since_execution > task.frequency:
        print(f"⚠️ Task {task.name} has not been run for {time_since_execution}, It is mean to run every {task.frequency}. running now if time is okay ...")
    elif old_report.status != SUCCESS:
        print(f"⚠️ Task {task.name} last run failed, running now if time is okay ...")
    else:
        print(f"Task `{task.name}` was run successfully {time_since_execution} ago, skipping...")
        return False, old_report

    suitable_run_time = task.start.time()
    time_now = datetime.now().time()
    min_diff = abs(suitable_run_time.hour - time_now.hour) * 60 + abs(suitable_run_time.minute - time_now.minute)
    if not min_diff < tolerance_mins:
        status = f"⌚ Time now is not suitable for running task {task.name} (Ideally, it should be run at {suitable_run_time})"
        print(status)
        return False, old_report
    return True, old_report


def run_task(task: Task) -> Report:
    start_time = datetime.now()

    shell_script = get_shell_script_executing_python_file(python_file=task.task_root.joinpath("task.py").str, ve_name=task.venv)
    shell_script_root = P.tmp().joinpath(f"tmp_scripts/scheduler/{task.name}").create()
    try:
        if platform.system() == 'Windows':
            shell_script = shell_script_root.joinpath("run.ps1").write_text(shell_script)
            subprocess.run(['powershell', '-ExecutionPolicy', 'Unrestricted', shell_script], check=True)
        elif platform.system() == 'Linux':
            shell_script = shell_script_root.joinpath("run.sh").write_text(shell_script)
            subprocess.run(['bash', shell_script], check=True)
        else: res = f"Error: Unsupported platform {platform.system()}."
        res = SUCCESS
    except subprocess.CalledProcessError: res = f"Error: The script {shell_script_root} failed to run."
    except Exception as e: res = f"Error: An unexpected error occurred while running the script {shell_script_root}: {e}"

    end_time = datetime.now()
    report = Report(name=task.name, start=start_time, end=end_time, status=res.replace('\n', '_NL_').strip().replace('=', '_eq_'))
    report.to_path(task.report_path)
    return report
