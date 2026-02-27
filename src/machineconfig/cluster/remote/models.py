from typing import Literal, TypeAlias
from dataclasses import dataclass, field, asdict
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

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict[str, object]) -> "WorkloadParams":
        return WorkloadParams(idx_min=int(d["idx_min"]), idx_max=int(d["idx_max"]), idx_start=int(d["idx_start"]), idx_end=int(d["idx_end"]), idx=int(d["idx"]), jobs=int(d["jobs"]), job_id=str(d["job_id"]))  # type: ignore[arg-type]

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

    def to_dict(self) -> dict[str, object]:
        return {"pid": self.pid, "job_id": self.job_id, "status": self.status, "submission_time": self.submission_time.isoformat(), "start_time": self.start_time.isoformat() if self.start_time else None}

    @staticmethod
    def from_dict(d: dict[str, object]) -> "JobStatus":
        return JobStatus(pid=int(d["pid"]), job_id=str(d["job_id"]), status=str(d["status"]), submission_time=datetime.fromisoformat(str(d["submission_time"])), start_time=datetime.fromisoformat(str(d["start_time"])) if d.get("start_time") else None)  # type: ignore[arg-type]


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

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = asdict(self)
        if self.workload_params is not None:
            d["workload_params"] = self.workload_params.to_dict()
        return d

    @staticmethod
    def from_dict(d: dict[str, object]) -> "RemoteMachineConfig":
        wl_raw = d.get("workload_params")
        wl = WorkloadParams.from_dict(wl_raw) if isinstance(wl_raw, dict) else None  # type: ignore[arg-type]
        return RemoteMachineConfig(
            job_id=str(d.get("job_id", "")), base_dir=str(d.get("base_dir", "~/tmp_results/remote_machines/jobs")), description=str(d.get("description", "")), ssh_host=str(d["ssh_host"]) if d.get("ssh_host") else None,
            copy_repo=bool(d.get("copy_repo", False)), update_repo=bool(d.get("update_repo", False)), install_repo=bool(d.get("install_repo", False)), data=list(d.get("data", [])),  # type: ignore[arg-type]
            transfer_method=str(d.get("transfer_method", "sftp")), cloud_name=str(d["cloud_name"]) if d.get("cloud_name") else None,  # type: ignore[assignment]
            allowed_remotes=list(d["allowed_remotes"]) if d.get("allowed_remotes") else None,  # type: ignore[arg-type]
            notify_upon_completion=bool(d.get("notify_upon_completion", False)), to_email=str(d["to_email"]) if d.get("to_email") else None, email_config_name=str(d["email_config_name"]) if d.get("email_config_name") else None,
            launch_method=str(d.get("launch_method", "remotely")), kill_on_completion=bool(d.get("kill_on_completion", False)), interactive=bool(d.get("interactive", False)),  # type: ignore[assignment]
            wrap_in_try_except=bool(d.get("wrap_in_try_except", False)), parallelize=bool(d.get("parallelize", False)), lock_resources=bool(d.get("lock_resources", True)), max_simultaneous_jobs=int(d.get("max_simultaneous_jobs", 1)),  # type: ignore[arg-type]
            workload_params=wl,
        )

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
