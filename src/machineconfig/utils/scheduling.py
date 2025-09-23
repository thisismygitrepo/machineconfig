# """Task scheduler
# """

# from machineconfig.utils.utils import get_shell_script_executing_python_file
# from machineconfig.utils.utils2 import read_ini
# from dataclasses import dataclass
# from datetime import datetime, timedelta
# from typing import Optional, Any
# from rich.console import Console
# from rich.panel import Panel
# import platform
# import subprocess


# def str2timedelta(time_str: str) -> timedelta:
#     """Convert string to timedelta. Simple implementation for common cases."""
#     # Handle common formats like "1h", "30m", "2d", etc.
#     import re

#     # Parse patterns like "1h", "30m", "2d", "1w"
#     match = re.match(r'^(\d+)([hdwm])$', time_str.lower())
#     if match:
#         value, unit = match.groups()
#         value = int(value)

#         if unit == 'h':
#             return timedelta(hours=value)
#         elif unit == 'd':
#             return timedelta(days=value)
#         elif unit == 'w':
#             return timedelta(weeks=value)
#         elif unit == 'm':
#             return timedelta(minutes=value)

#     # Fallback: try to parse as seconds
#     try:
#         return timedelta(seconds=int(time_str))
#     except ValueError:
#         raise ValueError(f"Cannot parse time string: {time_str}")


# def format_table_markdown(data: list[dict[str, Any]]) -> str:
#     """Convert list of dictionaries to markdown table format."""
#     if not data:
#         return ""

#     # Get all unique keys from all dictionaries
#     all_keys = set()
#     for row in data:
#         all_keys.update(row.keys())

#     keys = sorted(all_keys)

#     # Create header
#     header = "|" + "|".join(f" {key} " for key in keys) + "|"
#     separator = "|" + "|".join(" --- " for _ in keys) + "|"

#     # Create rows
#     rows = []
#     for row in data:
#         row_values = []
#         for key in keys:
#             value = row.get(key, "")
#             # Convert to string and handle None values
#             if value is None:
#                 value = ""
#             else:
#                 value = str(value)
#             row_values.append(f" {value} ")
#         rows.append("|" + "|".join(row_values) + "|")

#     return "\n".join([header, separator] + rows)


# SUCCESS = "success"
# DEFAULT_CONFIG = """
# [specs]
# frequency = 30d
# start = 2024-01-01 01:00

# [runtime]
# venv = ve
# """


# def save_ini(path: PathExtended, obj: dict[str, dict[str, Any]]) -> PathExtended:
#     """Write a simple INI file to `path` using standard library.

#     The `obj` should be a mapping of section name to a mapping of key/value pairs.
#     Values are converted to strings. The parent directory is created if missing.
#     Returns the resolved path.
#     """
#     import configparser

#     resolved_path: PathExtended = PathExtended(path).expanduser().absolute()
#     resolved_path.parent.mkdir(parents=True, exist_ok=True)

#     config = configparser.ConfigParser()
#     for section_name, section_values in obj.items():
#         # Ensure all values are stringified for configparser
#         config[section_name] = {str(k): ("" if v is None else str(v)) for k, v in section_values.items()}

#     with open(resolved_path, "w", encoding="utf-8") as file:
#         config.write(file)

#     return resolved_path


# class Register:
#     def __init__(self, root: str):
#         self.root = PathExtended(root).expanduser().absolute()

#     def register_runtime(self, frequency_months: int = 1):
#         start, end = self.get_report_start_end_datetimes(frequency_months=frequency_months)
#         report = Report(name="runtime", start=start, end=end, status="success")
#         report.to_path(self.root.joinpath("runtime.ini"))
#         return report

#     def read_runtime(self):
#         return Report.from_path(self.root.joinpath("runtime.ini"))

#     @staticmethod
#     def format_date(date: datetime):
#         return str(date.year)[2:] + "-" + str(date.month).zfill(2)
#     # @staticmethod
#     # def get_report_start_end_datetimes(frequency_months: int):
#     #     now = datetime.now()
#     #     import numpy as np
#     #     chunks = np.arange(start=1, stop=12, step=frequency_months)
#     #     chunk_now_start_month: int = chunks[chunks <= now.month][-1]
#     #     chunk_now_start = datetime(year=now.year, month=chunk_now_start_month, day=1)
#     #     from dateutil.relativedelta import relativedelta
#     #     previous_chunk_start = chunk_now_start - relativedelta(months=frequency_months)
#     #     return previous_chunk_start, chunk_now_start


# @dataclass
# class Report:
#     name: str
#     start: datetime
#     end: datetime
#     status: str

#     @classmethod
#     def from_path(cls, path: PathExtended, return_default_if_not_found: bool=False):
#         if not path.exists():
#             if return_default_if_not_found:
#                 return Report(name=path.parent.name, start=datetime(year=2000, month=1, day=1), end=datetime(year=2000, month=1, day=1), status="NA")
#             else:
#                 raise ValueError(f"Could not find report at {path}")
#         ini = read_ini(path)['report']
#         return cls(
#             name=ini["name"],
#             start=datetime.fromisoformat(ini["start"]),
#             end=datetime.fromisoformat(ini["end"]),
#             status=ini["status"],
#         )
#     def to_path(self, path: PathExtended):
#         save_ini(path=path, obj={
#             'report': {
#                 'name': self.name,
#                 'start': self.start.isoformat(),
#                 'end': self.end.isoformat(),
#                 'status': str(self.status),
#             }
#         })


# @dataclass
# class Task:
#     name: str
#     task_root: PathExtended
#     frequency: timedelta
#     start: datetime
#     venv: str
#     @property
#     def report_path(self):
#         return self.task_root.joinpath("report.ini")


# def read_task_from_dir(path: PathExtended):
#     tasks_config = read_ini(path.joinpath("config.ini"))
#     task = Task(name=path.name,
#                 task_root=path,
#                 frequency=str2timedelta(tasks_config["specs"]["frequency"]),
#                 start=datetime.fromisoformat(tasks_config["specs"]["start"]),
#                 venv=tasks_config["runtime"]["venv"],
#                 # output_dir=PathExtended(a_task_section["output_dir"]).expanduser().absolute(),
#                 )
#     return task


# def main(root: Optional[str] = None, ignore_conditions: bool=True):
#     if root is None: root_resolved = SCHEDULER_DEFAULT_ROOT
#     else: root_resolved = PathExtended(root).expanduser().absolute()
#     from pathlib import Path
#     # Find all `task.py` files under root and use their parent directories
#     tasks_dirs = list({PathExtended(p.parent) for p in Path(str(root_resolved)).rglob("task.py")})

#     # Print a fancy box using rich
#     console = Console()
#     console.print(Panel("TASK SCHEDULER INITIALIZED", title="Status", expand=False))

#     print(f"📁 Root directory resolved: {root_resolved}")

#     tasks: list[Task] = []
#     for a_dir in tasks_dirs:
#         tasks.append(read_task_from_dir(a_dir))

#     from machineconfig.utils.utils import choose_multiple_options

#     # Create data for tasks display
#     task_data = [Report.from_path(path=a_task.report_path).__dict__ for a_task in tasks]
#     task_display = format_table_markdown(task_data)
#     tasks_chosen_raw = choose_multiple_options(task_display.splitlines(), "📋 Choose tasks to run")
#     tasks_chosen = [tasks[int(a_task_chosen.split("|")[1])] for a_task_chosen in tasks_chosen_raw]

#     print(f"""
# 🎯 Selected Tasks:
# {task_display}
# """)

#     result: list[Report] = []
#     for a_task in tasks_chosen:
#         if not ignore_conditions:
#             answer, report = should_task_run(a_task)
#         else:
#             answer, report = True, None
#         if answer: report = run_task(a_task)
#         else:
#             assert report is not None
#         result.append(report)

#     result_data = [r.__dict__ for r in result]
#     result_display = format_table_markdown(result_data)
#     print(f"""
# ✅ Task Execution Results:
# {result_display}
# """)
#     return ""


# def should_task_run(task: Task, tolerance_mins: int = 1440) -> tuple[bool, Optional[Report]]:
#     if not task.report_path.exists():
#         print(f"""
# ⚠️  Task {task.name} has no record of being run before. Running now...
# """)
#         return True, None
#     old_report = Report.from_path(task.report_path)
#     time_since_execution = datetime.now() - old_report.end
#     if time_since_execution > task.frequency:
#         print(f"""
# ⚠️  Task {task.name} has not been run for {time_since_execution}. It is meant to run every {task.frequency}. Running now if time is okay...
# """)
#     elif old_report.status != SUCCESS:
#         print(f"""
# ⚠️  Task {task.name} last run failed. Running now if time is okay...
# """)
#     else:
#         print(f"""
# ✅ Task `{task.name}` was run successfully {time_since_execution} ago. Skipping...
# """)
#         return False, old_report

#     suitable_run_time = task.start.time()
#     time_now = datetime.now().time()
#     min_diff = abs(suitable_run_time.hour - time_now.hour) * 60 + abs(suitable_run_time.minute - time_now.minute)
#     if not min_diff < tolerance_mins:
#         status = f"⌚ Time now is not suitable for running task {task.name} (Ideally, it should be run at {suitable_run_time})"
#         print(f"""
# {status}
# """)
#         return False, old_report
#     return True, old_report


# def run_task(task: Task) -> Report:
#     start_time = datetime.now()

#     # Print a fancy box using rich
#     console = Console()
#     console.print(Panel("RUNNING TASK", title="Status", expand=False))

#     print(f"Task: {task.name}")

#     shell_script_root = PathExtended.tmp().joinpath(f"tmp_scripts/scheduler/{task.name}")
#     shell_script_root.mkdir(parents=True, exist_ok=True)
#     try:
#         if platform.system() == 'Windows':
#             shell_script = shell_script_root.joinpath("run.ps1").write_text(shell_script, encoding="utf-8")
#             subprocess.run(['powershell', '-ExecutionPolicy', 'Unrestricted', shell_script], check=True)
#         elif platform.system() in ['Linux', 'Darwin']:
#             shell_script = shell_script_root.joinpath("run.sh").write_text(shell_script, encoding="utf-8")
#             subprocess.run(['bash', shell_script], check=True)
#         else: res = f"Error: Unsupported platform {platform.system()}."
#         res = SUCCESS
#     except subprocess.CalledProcessError:
#         res = f"Error: The script {shell_script_root} failed to run."
#     except Exception as e:
#         res = f"Error: An unexpected error occurred while running the script {shell_script_root}: {e}"

#     end_time = datetime.now()
#     report = Report(name=task.name, start=start_time, end=end_time, status=res.replace('\n', '_NL_').strip().replace('=', '_eq_'))
#     report.to_path(task.report_path)

#     print(f"""
# ✅ Task {task.name} completed with status: {res}
# """)
#     return report
