
"""Task scheduler
"""

from crocodile.file_management import P, Read, str2timedelta, Save
from dataclasses import dataclass
from datetime import datetime, timedelta
# from crocodile.meta import Scheduler


ROOT = P.home().joinpath("dotfiles/config/scheduler/tasks.ini")


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
    @classmethod
    def from_path(cls, path: P):
        ini = Read.ini(path)['report']
        return cls(
            start=datetime.fromisoformat(ini["start"]),
            end=datetime.fromisoformat(ini["end"]),
        )
    def to_path(self, path: P):
        Save.ini(path=path, obj={'report': {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
        }})


def run_task(task: Task):
    suitable_run_time = task.start.time()
    time_now = datetime.now().time()
    min_diff = abs(suitable_run_time.hour - time_now.hour) * 60 + abs(suitable_run_time.minute - time_now.minute)
    if not min_diff < 60:
        print(f"⌚ Time now is not suitable for running task {task.name} (Ideally, it should be run at {suitable_run_time})")
        return


def main():
    tasks = Read.ini(ROOT)

    for a_section in tasks.sections():
        a_task_section = tasks[a_section]
        a_task = Task(
            name=a_section,
            script_path=P(a_task_section["script_path"]).expanduser().absolute(),
            frequency=str2timedelta(a_task_section["frequency"]),
            start=datetime.fromisoformat(a_task_section["start"]),
            output_dir=P(a_task_section["output_dir"]).expanduser().absolute(),
        )

        if not a_task.report_path.exists(): run_task(a_task)
        else:
            a_report = Report.from_path(a_task.report_path)
            time_since_execution = datetime.now() - a_report.end
            if time_since_execution > a_task.frequency:
                run_task(a_task)


if __name__ == "__main__":
    pass
