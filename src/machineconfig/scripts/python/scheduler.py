
"""Task scheduler
"""

from crocodile.file_management import P, Read, str2timedelta, Save
# from crocodile.meta import Terminal
from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import subprocess
# from crocodile.meta import Scheduler


ROOT = P.home().joinpath("dotfiles/config/scheduler/tasks.ini")


def run_shell_script(path: str) -> bool:
    try:
        if platform.system() == 'Windows':
            if not path.endswith('.ps1'):
                print(f"Error: The file {path} is not a PowerShell script.")
                return False
            subprocess.run(['powershell', '-ExecutionPolicy', 'Unrestricted', path], check=True)
        elif platform.system() == 'Linux':
            if not path.endswith('.sh'):
                print(f"Error: The file {path} is not a Bash script.")
                return False
            subprocess.run(['bash', path], check=True)
        else:
            print(f"Error: Unsupported platform {platform.system()}.")
            return False
        return True
    except subprocess.CalledProcessError:
        print(f"Error: The script {path} failed to run.")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred while running the script {path}: {e}")
        return False



@dataclass
class Task:
    name: str
    script_path: P
    frequency: timedelta
    start: datetime
    output_dir: P
    @property
    def report_path(self):
        return self.output_dir.joinpath(f"task_report_{self.name}.ini")


@dataclass
class Report:
    start: datetime
    end: datetime
    status: bool

    @classmethod
    def from_path(cls, path: P):
        ini = Read.ini(path)['report']
        return cls(
            start=datetime.fromisoformat(ini["start"]),
            end=datetime.fromisoformat(ini["end"]),
            status=ini["status"] == "True",
        )
    def to_path(self, path: P):
        Save.ini(path=path, obj={'report': {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'status': str(self.status),
        }})


def run_task(task: Task):
    suitable_run_time = task.start.time()
    time_now = datetime.now().time()
    min_diff = abs(suitable_run_time.hour - time_now.hour) * 60 + abs(suitable_run_time.minute - time_now.minute)
    if not min_diff < 60:
        print(f"⌚ Time now is not suitable for running task {task.name} (Ideally, it should be run at {suitable_run_time})")
        return
    start_time = datetime.now()
    # res = Terminal().run(task.script_path.str)
    res = run_shell_script(task.script_path.str)
    end_time = datetime.now()
    report = Report(start=start_time, end=end_time, status=res)
    report.to_path(task.report_path)


def main():
    tasks = Read.ini(ROOT)
    system = platform.system()

    for a_section in tasks.sections():
        a_task_section = tasks[a_section]
        a_task = Task(
            name=a_section,
            script_path=P(a_task_section["script_path"]).expanduser().absolute(),
            frequency=str2timedelta(a_task_section["frequency"]),
            start=datetime.fromisoformat(a_task_section["start"]),
            output_dir=P(a_task_section["output_dir"]).expanduser().absolute(),
        )

        if system == "Windows" and a_task.script_path.suffix != ".ps1":
            print(f"⚠️  Task {a_task.name} is not a powershell script, skipping...")
            continue
        elif system == "Linux" and a_task.script_path.suffix != ".sh":
            print(f"⚠️  Task {a_task.name} is not a bash script, skipping...")
            continue

        if not a_task.report_path.exists(): run_task(a_task)
        else:
            a_report = Report.from_path(a_task.report_path)
            time_since_execution = datetime.now() - a_report.end
            if time_since_execution > a_task.frequency:
                run_task(a_task)


if __name__ == "__main__":
    pass
