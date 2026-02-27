import os
import time
import platform
from pathlib import Path
from datetime import datetime

import psutil
from rich.console import Console

from machineconfig.utils.accessories import pprint
from machineconfig.utils.io import save_pickle, from_pickle
from machineconfig.cluster.remote.models import JOB_STATUS, MACHINE_TYPE, JobStatus

console = Console()

RUNNING_PATH = Path.home() / "tmp_results/remote_machines/file_manager/running_jobs.pkl"
QUEUE_PATH = Path.home() / "tmp_results/remote_machines/file_manager/queued_jobs.pkl"
HISTORY_PATH = Path.home() / "tmp_results/remote_machines/file_manager/history_jobs.pkl"
SHELL_SCRIPT_LOG_PATH = Path.home() / "tmp_results/remote_machines/file_manager/last_cluster_script.txt"
DEFAULT_BASE = Path.home() / "tmp_results/remote_machines/jobs"


class FileManager:
    def __init__(self, job_id: str, remote_machine_type: MACHINE_TYPE, lock_resources: bool, max_simultaneous_jobs: int, base: str | None) -> None:
        self.remote_machine_type: MACHINE_TYPE = remote_machine_type
        self.job_id = job_id
        self.max_simultaneous_jobs = max_simultaneous_jobs
        self.lock_resources = lock_resources
        self.submission_time = datetime.now()
        base_path = Path(base).expanduser() if base else DEFAULT_BASE
        self.base_dir = base_path
        self.job_root = self.base_dir / f"queued/{self.job_id}"

    def __getstate__(self) -> dict[str, object]:
        return self.__dict__

    def __setstate__(self, state: dict[str, object]) -> None:
        self.__dict__ = state

    @staticmethod
    def from_pickle_file(path: str | Path) -> "FileManager":
        state = from_pickle(Path(path).expanduser())
        fm = FileManager.__new__(FileManager)
        fm.__setstate__(state)
        return fm

    @property
    def py_script_path(self) -> Path:
        return self.job_root / "python/cluster_wrap.py"

    @property
    def cloud_download_py_script_path(self) -> Path:
        return self.job_root / "python/download_data.py"

    @property
    def shell_script_path(self) -> Path:
        ext = ".ps1" if self.remote_machine_type == "Windows" else ".sh"
        return self.job_root / f"shell/cluster_script{ext}"

    @property
    def kwargs_path(self) -> Path:
        return self.job_root / "data/func_kwargs.pkl"

    @property
    def file_manager_path(self) -> Path:
        return self.job_root / "data/file_manager.pkl"

    @property
    def remote_machine_path(self) -> Path:
        return self.job_root / "data/remote_machine.pkl"

    @property
    def remote_machine_config_path(self) -> Path:
        return self.job_root / "data/remote_machine_config.pkl"

    @property
    def execution_log_dir(self) -> Path:
        return self.job_root / "logs"

    def get_fire_command(self) -> str:
        script_path = self.shell_script_path.expanduser()
        local_system = platform.system()
        if local_system == "Windows" and script_path.suffix == ".sh":
            script_path = script_path.with_suffix(".ps1")
        elif local_system == "Linux" and script_path.suffix == ".ps1":
            script_path = script_path.with_suffix(".sh")
        return f". {script_path}"

    def get_job_status(self, session_name: str, tab_name: str) -> JOB_STATUS:
        log_dir = self.execution_log_dir.expanduser()
        pid_path = log_dir / "pid.txt"
        status_path = log_dir / "status.txt"
        if not status_path.exists():
            return "queued"
        status_text = status_path.read_text(encoding="utf-8").strip()
        status: JOB_STATUS = status_text  # type: ignore[assignment]
        if status != "running":
            return status
        if not pid_path.exists():
            print(f"Job `{self.job_id}` status says running but pid file missing. Marking failed.")
            _write_status(status_path, "failed")
            return "failed"
        pid = int(pid_path.read_text(encoding="utf-8").strip())
        try:
            proc = psutil.Process(pid=pid)
        except psutil.NoSuchProcess:
            print(f"Job `{self.job_id}` pid {pid} is dead. Marking failed.")
            _write_status(status_path, "failed")
            return "failed"
        command = " ".join(proc.cmdline())
        if self.job_id not in command:
            print(f"Job `{self.job_id}` pid {pid} belongs to different process: {command}. Marking failed.")
            _write_status(status_path, "failed")
            return "failed"
        print(f"Job `{self.job_id}` running with pid={pid}, session={session_name}, tab={tab_name}.")
        return "running"

    def secure_resources(self) -> bool:
        if not self.lock_resources:
            return True
        this_job = JobStatus(job_id=self.job_id, pid=os.getpid(), submission_time=self.submission_time, start_time=None, status="locked")
        sleep_time_secs = 600
        while True:
            running_file = _load_job_list(RUNNING_PATH)
            queue_file = self._add_to_queue(this_job)
            if len(running_file) < self.max_simultaneous_jobs:
                break
            running_file = _clean_dead_processes_from_list(running_file, RUNNING_PATH)
            if len(running_file) < self.max_simultaneous_jobs:
                break
            queue_file = _clean_dead_processes_from_list(queue_file, QUEUE_PATH)
            if not running_file:
                break
            running_job = running_file[0]
            assert running_job.start_time is not None
            now = datetime.now()
            pprint({"Submission time": this_job.submission_time, "Waiting": now - this_job.submission_time, f"Lock holder {running_job.job_id} running for": now - running_job.start_time}, f"Job `{this_job.job_id}` waiting")
            console.rule(f"Resources locked by `{running_job.job_id}`. Sleeping {sleep_time_secs // 60} min.", style="bold red")
            time.sleep(sleep_time_secs)
        self._write_lock_file(this_job)
        console.print(f"Resources locked by `{self.job_id}` (pid={os.getpid()}).", highlight=True)
        return True

    def unlock_resources(self) -> None:
        if not self.lock_resources:
            return
        running_file = _load_job_list(RUNNING_PATH)
        this_job = next((js for js in running_file if js.job_id == self.job_id), None)
        if this_job is not None:
            running_file.remove(this_job)
        else:
            print(f"Job {self.job_id} not in running file. File may be corrupt.")
        console.print(f"Resources released by `{self.job_id}`.")
        save_pickle(obj=running_file, path=RUNNING_PATH, verbose=False)
        start_time_path = self.execution_log_dir.expanduser() / "start_time.txt"
        if start_time_path.exists():
            start_time = datetime.fromisoformat(start_time_path.read_text(encoding="utf-8").strip())
            end_time = datetime.now()
            hist_file = HISTORY_PATH
            hist: list[dict[str, object]] = _load_pickle_or_default(hist_file, [])
            hist.append({"job_id": self.job_id, "start_time": start_time, "end_time": end_time, "submission_time": self.submission_time})
            save_pickle(obj=hist, path=hist_file, verbose=False)

    def get_resources_unlock_shell_cmd(self) -> str:
        collapsed = _collapse_user(RUNNING_PATH)
        return f"rm {collapsed}\necho 'Unlocked resources'"

    def _add_to_queue(self, job_status: JobStatus) -> list[JobStatus]:
        queue_file = _load_job_list(QUEUE_PATH)
        job_ids = [job.job_id for job in queue_file]
        if self.job_id not in job_ids:
            queue_file.append(job_status)
            save_pickle(obj=queue_file, path=QUEUE_PATH, verbose=False)
        return queue_file

    def _write_lock_file(self, job_status: JobStatus) -> None:
        job_status.start_time = datetime.now()
        queue_file = _load_job_list(QUEUE_PATH)
        if job_status in queue_file:
            queue_file.remove(job_status)
        save_pickle(obj=queue_file, path=QUEUE_PATH, verbose=False)
        running_file = _load_job_list(RUNNING_PATH)
        if len(running_file) >= self.max_simultaneous_jobs:
            raise RuntimeError(f"Running jobs ({len(running_file)}) >= max ({self.max_simultaneous_jobs}). Should not write lock.")
        running_file.append(job_status)
        save_pickle(obj=running_file, path=RUNNING_PATH, verbose=False)


def _write_status(path: Path, status: str) -> None:
    path.write_text(status, encoding="utf-8")


def _load_job_list(path: Path) -> list[JobStatus]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        save_pickle(obj=[], path=path, verbose=False)
        return []
    return from_pickle(path)


def _load_pickle_or_default[T](path: Path, default: T) -> T:
    if path.exists():
        return from_pickle(path)
    return default


def _clean_dead_processes_from_list(jobs: list[JobStatus], path: Path) -> list[JobStatus]:
    alive: list[JobStatus] = []
    changed = False
    for job in jobs:
        try:
            psutil.Process(pid=job.pid)
            alive.append(job)
        except psutil.NoSuchProcess:
            print(f"Process pid={job.pid} for job `{job.job_id}` is dead, removing.")
            changed = True
    if changed:
        save_pickle(obj=alive, path=path, verbose=False)
    return alive


def _collapse_user(p: Path) -> str:
    try:
        return "~/" + str(p.expanduser().resolve().relative_to(Path.home()))
    except ValueError:
        return str(p)
