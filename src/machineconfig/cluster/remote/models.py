from typing import Literal, TypeAlias
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from machineconfig.utils.accessories import randstr
from machineconfig.utils.io import read_ini
from machineconfig.utils.source_of_truth import DEFAULTS_PATH


JOB_STATUS: TypeAlias = Literal["queued", "running", "completed", "failed"]
TRANSFER_METHOD: TypeAlias = Literal["sftp", "cloud"]
LAUNCH_METHOD: TypeAlias = Literal["remotely", "cloud_manager"]
MACHINE_TYPE: TypeAlias = Literal["Linux", "Windows"]


@dataclass
class WorkloadParams:
    idx_min: int
    idx_max: int
    idx_start: int
    idx_end: int
    idx: int
    jobs: int
    job_id: str

    @property
    def save_suffix(self) -> str:
        return f"machine_{self.idx_start}_{self.idx_end}"

    def split_to_jobs(self, jobs: int) -> list["WorkloadParams"]:
        total_items = max(0, self.idx_end - self.idx_start)
        if total_items == 0:
            return []
        num_jobs = min(jobs, total_items)
        indices = list(range(self.idx_start, self.idx_end))
        result: list[WorkloadParams] = []
        for i in range(num_jobs):
            start_offset = (i * total_items) // num_jobs
            end_offset = ((i + 1) * total_items) // num_jobs
            chunk = indices[start_offset:end_offset]
            if not chunk:
                continue
            result.append(WorkloadParams(idx_start=chunk[0], idx_end=chunk[-1] + 1, idx_max=self.idx_max, jobs=self.jobs, idx=i, idx_min=self.idx_min, job_id=""))
        return result

    @staticmethod
    def default() -> "WorkloadParams":
        return WorkloadParams(idx_min=0, idx_max=1000, idx_start=0, idx_end=1000, idx=0, jobs=3, job_id="")

    def get_section_from_series(self, series: list[datetime]) -> tuple[datetime, datetime]:
        from math import floor
        min_idx_start = int(floor((len(series) - 1) * self.idx_start / self.idx_max))
        min_idx_end = int(floor((len(series) - 1) * self.idx_end / self.idx_max))
        return series[min_idx_start], series[min_idx_end]

    def print_summary(self) -> None:
        pct = (self.idx_end - self.idx_start) / self.idx_max * 100 if self.idx_max > 0 else 0
        print(f"Workload: {pct:.2f}% of total, split among {self.jobs} threads.")


@dataclass
class JobStatus:
    pid: int
    job_id: str
    status: Literal["locked", "unlocked"]
    submission_time: datetime
    start_time: datetime | None


@dataclass
class EmailParams:
    addressee: str
    speaker: str
    ssh_conn_str: str
    executed_obj: str
    email_config_name: str
    to_email: str
    file_manager_path: str


@dataclass
class LogEntry:
    name: str
    submission_time: str
    start_time: str | None
    end_time: str | None
    run_machine: str | None
    session_name: str | None
    pid: int | None
    cmd: str | None
    source_machine: str
    note: str

    @staticmethod
    def from_dict(a_dict: dict[str, object]) -> "LogEntry":
        return LogEntry(
            name=str(a_dict["name"]),
            submission_time=str(a_dict["submission_time"]),
            start_time=str(a_dict["start_time"]) if a_dict.get("start_time") else None,
            end_time=str(a_dict["end_time"]) if a_dict.get("end_time") else None,
            run_machine=str(a_dict["run_machine"]) if a_dict.get("run_machine") else None,
            source_machine=str(a_dict.get("source_machine", "")),
            note=str(a_dict.get("note", "")),
            pid=int(a_dict["pid"]) if a_dict.get("pid") is not None else None,  # type: ignore[arg-type]
            cmd=str(a_dict["cmd"]) if a_dict.get("cmd") else None,
            session_name=str(a_dict["session_name"]) if a_dict.get("session_name") else None,
        )


def _read_default_config_value(key: str) -> str:
    try:
        section = read_ini(DEFAULTS_PATH)["general"]
        return str(section[key])
    except (FileNotFoundError, KeyError, IndexError) as err:
        raise ValueError(f"Default config value '{key}' could not be read from `{DEFAULTS_PATH}`") from err


@dataclass
class RemoteMachineConfig:
    job_id: str = field(default_factory=lambda: randstr(noun=True))
    base_dir: str = "~/tmp_results/remote_machines/jobs"
    description: str = ""
    ssh_host: str | None = None

    copy_repo: bool = False
    update_repo: bool = False
    install_repo: bool = False
    data: list[str] = field(default_factory=list)
    transfer_method: TRANSFER_METHOD = "sftp"
    cloud_name: str | None = None

    allowed_remotes: list[str] | None = None
    notify_upon_completion: bool = False
    to_email: str | None = None
    email_config_name: str | None = None

    launch_method: LAUNCH_METHOD = "remotely"
    kill_on_completion: bool = False
    interactive: bool = False
    wrap_in_try_except: bool = False
    parallelize: bool = False
    lock_resources: bool = True
    max_simultaneous_jobs: int = 1
    workload_params: WorkloadParams | None = None

    def __post_init__(self) -> None:
        if self.interactive and self.lock_resources:
            print("⚠️ RemoteMachineConfig: interactive + lock_resources means the job might never release the lock.")
        if self.transfer_method == "cloud" and self.cloud_name is None:
            raise ValueError("cloud_name must be provided when transfer_method is 'cloud'")
        if self.notify_upon_completion:
            if self.to_email is None:
                self.to_email = _read_default_config_value("to_email")
            if self.email_config_name is None:
                self.email_config_name = _read_default_config_value("email_config_name")


@dataclass
class ExecutionTimings:
    start_utc: datetime
    end_utc: datetime
    start_local: datetime
    end_local: datetime
    submission_time: datetime

    @property
    def execution_duration(self) -> timedelta:
        return self.end_utc - self.start_utc

    @property
    def wait_duration(self) -> timedelta:
        return self.start_local - self.submission_time
