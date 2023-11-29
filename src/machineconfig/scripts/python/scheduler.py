
"""Task scheduler
"""

from crocodile.file_management import P, Read, str2timedelta, Save
# from crocodile.meta import Terminal
from machineconfig.utils.utils import CONFIG_PATH, get_shell_script_executing_python_file
from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import subprocess
from typing import Optional
# from crocodile.meta import Scheduler


SCHEDULER_DEFAULT_ROOT = P.home().joinpath("dotfiles/.scheduler")
SUCCESS = "success"


@dataclass
class Report:
    name: str
    start: datetime
    end: datetime
    status: str

    @classmethod
    def from_path(cls, path: P):
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
        return CONFIG_PATH.joinpath("scheduler", self.task_root.rel2home().joinpath("report.ini"))


def task_to_report(task: Task):
    if task.report_path.exists(): return Report.from_path(task.report_path)
    return Report(name=task.name, start=datetime(year=2000, month=1, day=1), end=datetime(year=2000, month=1, day=1), status="NA")


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
    tasks = []
    for a_dir in tasks_dirs:
        tasks.append(read_task_from_dir(a_dir))

    from machineconfig.utils.utils import choose_multiple_options
    import pandas as pd
    df_res = pd.DataFrame([task_to_report(a_task).__dict__ for a_task in tasks])
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
    root_resolved.joinpath("task_report.md").write_text(df_res.to_markdown(), encoding="utf-8")
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


def main_parse():
    import argparse
    parser = argparse.ArgumentParser(description='Run tasks.')
    parser.add_argument('--root', '-r', type=str, default=None, help='Root directory of tasks.')
    parser.add_argument('--ignore_conditions', "-i", action='store_true', help='Ignore conditions for running tasks.', default=False)
    parser.add_argument('--report', "-R", action='store_true', help='Print report.', default=False)
    print(parser)
    args = parser.parse_args()

    if P(args.root).search(files=False, folders=True)[0].joinpath("task.py").exists():
        root = str(args.root)
    elif P(args.root).joinpath(".scheduler").search(files=False, folders=True)[0].joinpath("task.py").exists():
        root = P(args.root).joinpath(".scheduler").str
    else:
        raise ValueError(f"Could not find a task.py in {args.root} or {P(args.root).joinpath('.scheduler')}")

    if args.report:
        report = P(root).joinpath("task_report.md").read_text(encoding="utf-8")
        print(report)
        return None

    main(root=root, ignore_conditions=args.ignore_conditions)


if __name__ == "__main__":
    pass
