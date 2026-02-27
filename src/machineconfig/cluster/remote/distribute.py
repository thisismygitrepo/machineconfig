from __future__ import annotations

from typing import Callable
from math import floor
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from copy import deepcopy

from rich.console import Console

from machineconfig.utils.accessories import randstr, pprint
from machineconfig.utils.io import save_pickle
from machineconfig.utils.ssh import SSH
from machineconfig.cluster.remote.models import RemoteMachineConfig, WorkloadParams
from machineconfig.cluster.remote.remote_machine import RemoteMachine

console = Console()


class LoadCriterion(Enum):
    cpu = "cpu"
    ram = "ram"
    product = "cpu * ram"
    cpu_norm = "cpu_norm"
    ram_norm = "ram_norm"
    product_norm = "cpu_norm * ram_norm"


@dataclass
class MachineSpecs:
    cpu: float
    ram: float
    product: float
    cpu_norm: float
    ram_norm: float
    product_norm: float

    @staticmethod
    def from_local() -> MachineSpecs:
        import psutil
        cpu = psutil.cpu_count() or 1
        ram = psutil.virtual_memory().total / 2**30
        return MachineSpecs(cpu=float(cpu), ram=ram, product=cpu * ram, cpu_norm=float(cpu), ram_norm=ram, product_norm=cpu * ram)


@dataclass
class ThreadLoadCalculator:
    num_jobs: int | None
    load_criterion: LoadCriterion
    reference_specs: MachineSpecs

    @staticmethod
    def default() -> ThreadLoadCalculator:
        return ThreadLoadCalculator(num_jobs=None, load_criterion=LoadCriterion.cpu, reference_specs=MachineSpecs.from_local())

    def get_num_threads(self, machine_specs: MachineSpecs) -> int:
        if self.num_jobs is None:
            return 1
        ref_val = getattr(self.reference_specs, self.load_criterion.name)
        machine_val = getattr(machine_specs, self.load_criterion.name)
        if ref_val == 0:
            return 1
        res = int(floor(self.num_jobs * (machine_val / ref_val)))
        return max(1, res)


class MachineLoadCalculator:
    def __init__(self, max_num: int, load_criterion: LoadCriterion) -> None:
        self.load_ratios: list[float] = []
        self.max_num = max_num
        self.load_criterion = load_criterion

    def get_workload_params(self, machines_specs: list[MachineSpecs], threads_per_machine: list[int]) -> list[WorkloadParams]:
        result: list[WorkloadParams] = []
        idx_so_far = 0
        for machine_idx, (specs, threads) in enumerate(zip(machines_specs, threads_per_machine)):
            load_value = getattr(specs, self.load_criterion.name)
            self.load_ratios.append(load_value)
            idx1 = idx_so_far
            if machine_idx == len(threads_per_machine) - 1:
                idx2 = self.max_num
            else:
                idx2 = floor(load_value * self.max_num) + idx1
            if idx2 > self.max_num:
                raise ValueError(f"Computed idx_end ({idx2}) > max_num ({self.max_num})")
            idx_so_far = idx2
            result.append(WorkloadParams(idx_start=idx1, idx_end=idx2, idx_max=self.max_num, jobs=threads, idx=machine_idx, idx_min=0, job_id=""))
        return result


class Cluster:
    def __init__(
        self,
        func: Callable[..., object],
        ssh_hosts: list[str],
        config: RemoteMachineConfig,
        func_kwargs: dict[str, object],
        thread_load_calc: ThreadLoadCalculator,
        ditch_unavailable: bool,
        description: str,
        job_id: str | None,
        base_dir: str | None,
    ) -> None:
        self.job_id = job_id or randstr(noun=True)
        self.root_dir = _get_cluster_path(self.job_id, base_dir)
        self.results_downloaded = False
        self.thread_load_calc = thread_load_calc
        norm_criterion_name = self.thread_load_calc.load_criterion.name + "_norm"
        self.machine_load_calc = MachineLoadCalculator(max_num=1000, load_criterion=LoadCriterion[norm_criterion_name])
        self.ssh_connections: list[SSH] = []
        for host in ssh_hosts:
            try:
                self.ssh_connections.append(SSH.from_config_file(host=host))
            except Exception as ex:
                print(f"Cannot connect to {host}")
                if not ditch_unavailable:
                    raise ConnectionError(f"Cannot connect to {host}") from ex
        self.machines: list[RemoteMachine] = []
        self.machines_specs: list[MachineSpecs] = []
        self.threads_per_machine: list[int] = []
        self.config = config
        self.workload_params: list[WorkloadParams] = []
        self.description = description
        self.func = func
        self.func_kwargs = func_kwargs

    def __repr__(self) -> str:
        items = self.machines if self.machines else self.ssh_connections
        return "Cluster:\n" + "\n".join(repr(x) for x in items)

    def generate_standard_kwargs(self) -> None:
        if self.workload_params:
            print("workload_params already set, skipping generation.")
            return
        cpus: list[float] = []
        rams: list[float] = []
        for ssh in self.ssh_connections:
            res = ssh.run_py_remotely(python_code="import psutil; print(psutil.cpu_count(), psutil.virtual_memory().total)", uv_with=None, uv_project_dir=None, description="get machine specs", verbose_output=False, strict_stderr=False, strict_return_code=False)
            parts = res.op.strip().split()
            cpus.append(float(parts[0]))
            rams.append(float(parts[1]) / 2**30)
        total_cpu = sum(cpus)
        total_ram = sum(rams)
        total_product = sum(c * r for c, r in zip(cpus, rams))
        self.machines_specs = [
            MachineSpecs(cpu=c, ram=r, product=c * r, cpu_norm=c / total_cpu if total_cpu else 0, ram_norm=r / total_ram if total_ram else 0, product_norm=(c * r) / total_product if total_product else 0)
            for c, r in zip(cpus, rams)
        ]
        self.threads_per_machine = [self.thread_load_calc.get_num_threads(specs) for specs in self.machines_specs]
        self.workload_params = self.machine_load_calc.get_workload_params(machines_specs=self.machines_specs, threads_per_machine=self.threads_per_machine)
        for ssh, wl in zip(self.ssh_connections, self.workload_params):
            pprint(wl.__dict__, ssh.get_remote_repr())

    def submit(self) -> None:
        if not self.workload_params:
            raise RuntimeError("Generate standard kwargs first.")
        for idx, (wl, ssh) in enumerate(zip(self.workload_params, self.ssh_connections)):
            cfg = deepcopy(self.config)
            cfg.description = self.description
            cfg.job_id = f"{self.job_id}_{idx}"
            cfg.base_dir = str(self.root_dir)
            cfg.workload_params = wl
            cfg.ssh_host = ssh.host or f"{ssh.username}@{ssh.hostname}"
            m = RemoteMachine(func=self.func, func_kwargs=self.func_kwargs, config=cfg, data=None)
            m.ssh = ssh
            m.generate_scripts()
            m.submit()
            self.machines.append(m)
        self._save()

    def fire(self, run: bool) -> None:
        for m in self.machines:
            m.fire(run=run)

    def run(self, run: bool) -> "Cluster":
        self.generate_standard_kwargs()
        self.submit()
        self.fire(run=run)
        self._save()
        return self

    def check_job_status(self) -> None:
        for m in self.machines:
            m.check_job_status()

    def download_results(self) -> None:
        all_done = True
        for m in self.machines:
            if m.results_path is None:
                print(f"Results not ready for {m}. Check status first.")
                all_done = False
                continue
            if not m.results_downloaded:
                console.rule(f"Downloading from {m}")
                m.download_results(target=None)
        if all_done and all(m.results_downloaded for m in self.machines):
            self.results_downloaded = True
            print(f"All results downloaded to {self.root_dir}")

    def _save(self) -> Path:
        path = self.root_dir / "cluster.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        state = self.__dict__.copy()
        state["func"] = None
        state["ssh_connections"] = []
        save_pickle(obj=state, path=path, verbose=False)
        return path

    @staticmethod
    def load(job_id: str, base_dir: str | None) -> Cluster:
        path = _get_cluster_path(job_id, base_dir) / "cluster.pkl"
        from machineconfig.utils.io import from_pickle
        state = from_pickle(path)
        cluster = Cluster.__new__(Cluster)
        cluster.__dict__ = state
        return cluster


def _get_cluster_path(job_id: str, base_dir: str | None) -> Path:
    if base_dir is None:
        return Path.home() / f"tmp_results/remote_machines/job_id__{job_id}"
    return Path(base_dir) / f"job_id__{job_id}"
