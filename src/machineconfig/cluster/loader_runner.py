
"""
Runner
"""

from rich.console import Console
import pandas as pd

from crocodile.core import List as L, Struct as S, randstr
from crocodile.file_management_helpers.file4 import Read
from crocodile.meta import SSH
from machineconfig.cluster.self_ssh import SelfSSH

from typing import Optional, Any, Literal, TypeAlias, Union
from dataclasses import dataclass, field


JOB_STATUS: TypeAlias = Literal["queued", "running", "completed", "failed"]
TRANSFER_METHOD: TypeAlias = Literal["sftp", "transfer_sh", "cloud"]
LAUNCH_METHOD: TypeAlias = Literal["remotely", "cloud_manager"]
console = Console()


@dataclass
class WorkloadParams:
    idx_min: int = 0
    idx_max: int = 1000
    idx_start: int = 0
    idx_end: int = 1000
    idx: int = 0
    jobs: int = 3
    job_id: str = ''
    @property
    def save_suffix(self) -> str: return f"machine_{self.idx_start}_{self.idx_end}"
    def split_to_jobs(self, jobs: Optional[int] = None) -> L['WorkloadParams']:
        # Note: like MachineLoadCalculator get_kwargs, the behaviour is to include the edge cases on both ends of subsequent intervals.
        res = L(range(self.idx_start, self.idx_end, 1)).split(to=jobs or self.jobs).apply(lambda sub_list: WorkloadParams(idx_start=sub_list.list[0], idx_end=sub_list.list[-1] + 1, idx_max=self.idx_max, jobs=self.jobs))
        for idx, item in enumerate(res): item.idx = idx
        return res
    def get_section_from_series(self, series: list[pd.Timestamp]):
        from math import floor
        min_idx_start = int(floor((len(series) - 1) * self.idx_start / self.idx_max))
        min_idx_end = int(floor((len(series) - 1) * self.idx_end / self.idx_max))
        min_start = series[min_idx_start]
        min_end = series[min_idx_end]
        return min_start, min_end
    def print(self): S(self.__dict__).print(as_config=True, title="Job Workload")
    def viz(self):
        print(f"This machine will execute ({(self.idx_end - self.idx_start) / self.idx_max * 100:.2f}%) of total job workload.")
        print(f"This share of workload will be split among {self.jobs} of threads on this machine.")


@dataclass
class JobStatus:
    pid: int
    job_id: str
    status: Literal['locked', 'unlocked']
    submission_time: pd.Timestamp
    start_time: Optional[pd.Timestamp] = None


@dataclass
class EmailParams:
    addressee: str
    speaker: str
    ssh_conn_str: str
    executed_obj: str
    email_config_name: str
    to_email: str
    file_manager_path: str
    @staticmethod
    def from_empty() -> 'EmailParams': return EmailParams(addressee="", speaker="", ssh_conn_str="", executed_obj="", email_config_name="", to_email="", file_manager_path="")


@dataclass
class LogEntry:
    name: str
    submission_time: str
    start_time: Optional[str]
    end_time: Optional[str]
    run_machine: Optional[str]
    session_name: Optional[str]
    pid: Optional[int]
    cmd: Optional[str]
    source_machine: str
    note: str
    @staticmethod
    def from_dict(a_dict: dict[str, Any]):
        return LogEntry(name=a_dict["name"], submission_time=pd.to_datetime(a_dict["submission_time"]), start_time=pd.to_datetime(a_dict["start_time"]), end_time=pd.to_datetime(a_dict["end_time"]),
                        run_machine=a_dict["run_machine"], source_machine=a_dict["source_machine"], note=a_dict["note"], pid=a_dict["pid"], cmd=a_dict["cmd"], session_name=a_dict["session_name"])



@dataclass
class RemoteMachineConfig:
    # conn
    job_id: str = field(default_factory=lambda: randstr(noun=True))
    base_dir: str = "~/tmp_results/remote_machines/jobs"
    description: str = ""
    ssh_params: dict[str, Union[str, int]] = field(default_factory=lambda: {})
    ssh_obj: Union[SSH, 'SelfSSH', None] = None

    # data
    copy_repo: bool = False
    update_repo: bool = False
    install_repo: bool = False
    update_essential_repos: bool = True
    data: Optional[list[Any]] = None
    transfer_method: TRANSFER_METHOD = "sftp"
    cloud_name: Optional[str] = None

    # remote machine behaviour
    allowed_remotes: Optional[list[str]] = None
    open_console: bool = True
    notify_upon_completion: bool = False
    to_email: Optional[str] = None
    email_config_name: Optional[str] = None

    # execution behaviour
    launch_method: LAUNCH_METHOD = "remotely"
    kill_on_completion: bool = False
    ipython: bool = False
    interactive: bool = False
    pdb: bool = False
    pudb: bool = False
    wrap_in_try_except: bool = False
    parallelize: bool = False
    lock_resources: bool = True
    max_simulataneous_jobs: int = 1
    workload_params: Optional[WorkloadParams] = None
    def __post_init__(self) -> None:
        if self.interactive and self.lock_resources: print("RemoteMachineConfig Warning: If interactive is ON along with lock_resources, the job might never end. ⚠️")
        if self.transfer_method == "cloud": assert self.cloud_name is not None, "Cloud name is not provided. 🤷‍♂️"
        if self.notify_upon_completion and self.to_email is None:
            from machineconfig.utils.utils import DEFAULTS_PATH
            try:
                section = Read.ini(DEFAULTS_PATH)['general']
                self.to_email = section['to_email']
            except (FileNotFoundError, KeyError, IndexError) as err: raise ValueError(f"Email address is not provided. 🤷‍♂️ & default could not be read @ `{DEFAULTS_PATH}`") from err
        if self.notify_upon_completion and self.email_config_name is None:
            from machineconfig.utils.utils import DEFAULTS_PATH
            try:
                section = Read.ini(DEFAULTS_PATH)['general']
                self.email_config_name = section['email_config_name']
            except (FileNotFoundError, KeyError, IndexError) as err: raise ValueError(f"Email config name is not provided. 🤷‍♂️ & default could not be read @ `{DEFAULTS_PATH}`") from err



if __name__ == '__main__':
    pass
