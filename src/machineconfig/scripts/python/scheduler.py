
"""Task scheduler
"""

from crocodile.file_management import P, Read, str2timedelta, Save
# from crocodile.meta import Terminal
from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import subprocess
from typing import Optional
# from crocodile.meta import Scheduler


ROOT = P.home().joinpath("dotfiles/scripts/tasks")
SUCCESS = "success"


def run_shell_script(path: str) -> str:
    try:
        if platform.system() == 'Windows':
            if not path.endswith('.ps1'): return f"Error: The file {path} is not a PowerShell script."
            subprocess.run(['powershell', '-ExecutionPolicy', 'Unrestricted', path], check=True)
        elif platform.system() == 'Linux':
            if not path.endswith('.sh'): return f"Error: The file {path} is not a Bash script."
            subprocess.run(['bash', path], check=True)
        else: return f"Error: Unsupported platform {platform.system()}."
        return SUCCESS
    except subprocess.CalledProcessError: return f"Error: The script {path} failed to run."
    except Exception as e: return f"Error: An unexpected error occurred while running the script {path}: {e}"


def create_shell_script(py_file: str):
    pass


@dataclass
class Task:
    name: str
    script_path: P
    frequency: timedelta
    start: datetime
    venv: str
    # output_dir: P
    # @property
    # def report_path(self):
    #     return self.output_dir.joinpath(f"task_report_{self.name}.ini")


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


def read_task_from_dir(path: P):
    tasks_config = Read.ini(path)
    task = Task(name=path.name,
                script_path=path,
                frequency=str2timedelta(tasks_config["config"]["frequency"]),
                start=datetime.fromisoformat(tasks_config["config"]["start"]),
                venv=tasks_config["runtime"]["venv"],
                # output_dir=P(a_task_section["output_dir"]).expanduser().absolute(),
                )
    return task


def main(task: Optional[str] = None):
    tasks_dirs = ROOT.search()
    tasks = [read_task_from_dir(a_dir) for a_dir in tasks_dirs]

    if task is None:  # choose manually
        from machineconfig.utils.utils import choose_multiple_options
        tasks_names = choose_multiple_options(tasks_names, "Choose tasks to run")

    result: list[Report] = []
    for a_section in tasks_names:
        a_task_section = tasks_config[a_section]

        if not a_task.report_path.exists():
            report = run_task(a_task)
            result.append(report)
        else:
            old_report = Report.from_path(a_task.report_path)
            time_since_execution = datetime.now() - old_report.end
            if time_since_execution > a_task.frequency:
                print(f"⚠️ Task {a_task.name} has not been run for {time_since_execution}, running now...")
                report = run_task(a_task)
                result.append(report)
            elif old_report.status != SUCCESS:
                print(f"⚠️ Task {a_task.name} last run failed, running now...")
                report = run_task(a_task)
                result.append(report)
    import pandas as pd
    df_res = pd.DataFrame([r.__dict__ for r in result])
    print(df_res)
    ROOT.with_name("task_report.md").write_text(df_res.to_markdown(), encoding="utf-8")
    return ""


def run_task(task: Task, tolerance_mins: int = 60):
    suitable_run_time = task.start.time()
    time_now = datetime.now().time()
    min_diff = abs(suitable_run_time.hour - time_now.hour) * 60 + abs(suitable_run_time.minute - time_now.minute)
    if not min_diff < tolerance_mins:
        status = f"⌚ Time now is not suitable for running task {task.name} (Ideally, it should be run at {suitable_run_time})"
        report = Report(name=task.name, start=datetime.now(), end=datetime.now(), status=status)
        return report
    start_time = datetime.now()
    # res = Terminal().run(task.script_path.str)
    res = run_shell_script(task.script_path.str)
    end_time = datetime.now()
    report = Report(name=task.name, start=start_time, end=end_time, status=res.replace('\n', '_NL_').strip().replace('=', '_eq_'))
    report.to_path(task.report_path)
    return report


if __name__ == "__main__":
    pass
