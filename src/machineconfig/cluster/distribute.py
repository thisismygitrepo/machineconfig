# """
# Distributed Computing
# """


# from typing import Optional, Any, Callable, Union
# from math import ceil, floor
# from enum import Enum
# from dataclasses import dataclass
# import psutil

# from machineconfig.utils.utils2 import randstr
# from machineconfig.utils.io_save import save_pickle
# from machineconfig.cluster.remote_machine import RemoteMachine, RemoteMachineConfig, WorkloadParams, LAUNCH_METHOD
# from rich.console import Console
# from machineconfig.utils.utils2 import pprint
# import io
# # from platform import system
# # import time
# # from rich.progress import track


# console = Console()


# class LoadCriterion(Enum):
#     cpu = "cpu"
#     ram = "ram"
#     product = "cpu * ram"
#     cpu_norm = "cpu_norm"
#     ram_norm = "ram_norm"
#     product_norm = "cpu_norm * ram_norm"


# @dataclass
# class MachineSpecs:
#     cpu: float
#     ram: float
#     product: float
#     cpu_norm: float
#     ram_norm: float
#     product_norm: float
#     @staticmethod
#     def get_this_machine_specs():
#         cpu, ram = psutil.cpu_count(), psutil.virtual_memory().total / 2 ** 30
#         assert cpu is not None
#         return MachineSpecs(cpu=cpu, ram=ram, product=cpu * ram, cpu_norm=cpu, ram_norm=ram, product_norm=cpu * ram)


# class ThreadLoadCalculator:
#     """relies on relative values to a referenc machine specs.
#     Runs multiple instances of code per machine. Useful if code doesn't run faster with more resources avaliable.
#     equal distribution across instances of one machine"""
#     def __init__(self, num_jobs: Optional[int] = None, load_criterion: LoadCriterion = LoadCriterion.cpu, reference_specs: Optional[MachineSpecs] = None):
#         self.num_jobs = num_jobs
#         self.load_criterion = load_criterion
#         self.reference_specs: MachineSpecs = MachineSpecs.get_this_machine_specs() if reference_specs is None else reference_specs
#     def __getstate__(self): return self.__dict__
#     def __setstate__(self, state: dict[str, Any]): self.__dict__.update(state)
#     def get_num_threads(self, machine_specs: MachineSpecs) -> int:
#         if self.num_jobs is None: return 1
#         res = int(floor(self.num_jobs * (machine_specs.__dict__[self.load_criterion.name] / self.reference_specs.__dict__[self.load_criterion.name])))
#         return 1 if res == 0 else res


# class MachineLoadCalculator:
#     def __init__(self, max_num: int = 1000, load_criterion: LoadCriterion = LoadCriterion.product, load_ratios_repr: str = ""):
#         self.load_ratios: list[float] = []
#         self.load_ratios_repr = load_ratios_repr
#         self.max_num: int = max_num
#         self.load_criterion = load_criterion
#     def __getstate__(self) -> dict[str, Any]: return self.__dict__
#     def __setstate__(self, d: dict[str, Any]) -> None: self.__dict__.update(d)
#     def get_workload_params(self, machines_specs: list[MachineSpecs], threads_per_machine: list[int]) -> list[WorkloadParams]:
#         """Note: like thread divider in parallelize function, the behaviour is to include the edge cases on both ends of subsequent intervals."""
#         tmp: list[WorkloadParams] = []
#         idx_so_far = 0
#         for machine_index, (machine_specs, a_threads_per_machine) in enumerate(zip(machines_specs, threads_per_machine)):
#             load_value = machine_specs.__dict__[self.load_criterion.name]
#             self.load_ratios.append(load_value)
#             idx1 = idx_so_far
#             idx2 = self.max_num if machine_index == len(threads_per_machine) - 1 else (floor(load_value * self.max_num) + idx1)
#             if idx2 > self.max_num:
#                 print(machines_specs, '\n\n', threads_per_machine)
#                 print(f"All values: {tmp=}, {idx_so_far=}, {idx1=}, {idx2=}, {self.max_num=}, {a_threads_per_machine=}, {machine_index=}, {machine_specs=}, {load_value=}, {self.load_ratios=}, {self.load_ratios_repr=}")
#                 raise ValueError(f"idx2 ({idx2}) > max_num ({self.max_num})")
#             idx_so_far = idx2
#             tmp.append(WorkloadParams(idx_start=idx1, idx_end=idx2, idx_max=self.max_num, jobs=a_threads_per_machine))
#         return tmp


# class Cluster:
#     def __getstate__(self) -> dict[str, Any]:
#         state = self.__dict__
#         state["func"] = None
#         return state
#     def __setstate__(self, state: dict[str, Any]) -> None: self.__dict__.update(state)
#     def save(self) -> P:
#         path = self.root_dir.joinpath("cluster.Cluster.pkl")
#         save_pickle(obj=self.__getstate__(), path=path)
#         return path
#     @staticmethod
#     def load(job_id: str, base: Optional[str] = None) -> 'Cluster': return Cluster.get_cluster_path(job_id=job_id, base=base).joinpath("cluster.Cluster.pkl").readit()
#     @staticmethod
#     def get_cluster_path(job_id: str, base: Union[str, P, None] = None):
#         if base is None: base_obj = PathExtended.home().joinpath("tmp_results/remote_machines")
#         else: base_obj = PathExtended(base)
#         return base_obj.joinpath(f"job_id__{job_id}")
#     def __init__(self,
#                  func: Callable[..., Any],
#                  ssh_params: list[dict[str, Any]],
#                  remote_machine_config: RemoteMachineConfig,
#                  func_kwargs: Optional[dict[str, Any]] = None,
#                  # workload_params: list[WorkloadParams] or None = None,
#                  thread_load_calc: Optional[ThreadLoadCalculator] = None,
#                  # machine_load_calc=None,
#                  ditch_unavailable_machines: bool = False,
#                  description: str = "",
#                  job_id: Optional[str] = None,
#                  base_dir: Union[str, P, None] = None):
#         self.job_id = job_id or randstr(noun=True)
#         self.root_dir = self.get_cluster_path(self.job_id, base=base_dir)
#         self.results_downloaded = False

#         self.thread_load_calc: ThreadLoadCalculator = thread_load_calc or ThreadLoadCalculator()
#         self.machine_load_calc: MachineLoadCalculator = MachineLoadCalculator(load_criterion=LoadCriterion[self.thread_load_calc.load_criterion.name + "_norm"], )

#         sshz: list[SSH] = []
#         for an_ssh_params in ssh_params:
#             try:
#                 tmp = SSH(**an_ssh_params)
#                 sshz.append(tmp)
#             except Exception as ex:
#                 print(f"Couldn't connect to {an_ssh_params}")
#                 if ditch_unavailable_machines: continue
#                 else: raise Exception(f"Couldn't connect to {an_ssh_params}") from ex  # type: ignore # pylint: disable=W0719

#         # lists of similar length:
#         self.sshz: list[SSH] = sshz
#         self.machines: list[RemoteMachine] = []
#         self.machines_specs: list[MachineSpecs] = []
#         self.threads_per_machine: list[int] = []
#         self.remote_machine_kwargs: RemoteMachineConfig = remote_machine_config
#         self.workload_params: list[WorkloadParams] = []

#         self.description: str = description
#         self.func = func
#         self.func_kwargs = func_kwargs if func_kwargs is not None else {}

#         # fire options
#         self.machines_per_tab: int = 1
#         self.window_number: int = 2

#     def __repr__(self): return "Cluster with following machines:\n" + "\n".join([repr(item) for item in (self.machines if self.machines else self.sshz)])
#     def print_func_kwargs(self):
#         print("\n" * 2)
#         console.rule(title="kwargs of functions to be run on machines")
#         for an_ssh, a_kwarg in zip(self.sshz, self.workload_params):
#             pprint(a_kwarg.__dict__, an_ssh.get_remote_repr())
#     def print_commands(self, launch_method: LAUNCH_METHOD):
#         print("\n" * 2)
#         console.rule(title="Commands to run on each machine:")
#         for machine in self.machines:
#             print(f"{repr(machine)} ==> {machine.file_manager.get_fire_command(launch_method=launch_method)}")

#     def generate_standard_kwargs(self) -> None:
#         if self.workload_params:
#             self.print_func_kwargs()
#             print(self.workload_params, len(self.workload_params), type(self.workload_params))
#             print("workload_params is not None, so not generating standard kwargs")
#             return None
#         cpus: list[float] = []
#         rams: list[float] = []
#         for an_ssh in self.sshz:
#             res = an_ssh.run_py("import psutil; print(psutil.cpu_count(), psutil.virtual_memory().total)", verbose=False).op
#             try: cpus.append(int(res.split(' ')[0]))
#             except ValueError as ve:
#                 print(f"Couldn't get cpu count from {an_ssh}")
#                 raise ValueError(f"Couldn't get cpu count from {an_ssh.get_remote_repr()}") from ve
#             rams.append(ceil(int(res.split(' ')[1]) / 2 ** 30))
#         total_cpu = np.array(cpus).sum()
#         total_ram = np.array(rams).sum()
#         total_product = (np.array(cpus) * np.array(rams)).sum()

#         self.machines_specs = [MachineSpecs(cpu=a_cpu, ram=a_ram, product=a_cpu * a_ram, cpu_norm=a_cpu / total_cpu, ram_norm=a_ram / total_ram, product_norm=a_cpu * a_ram / total_product) for a_cpu, a_ram in zip(cpus, rams)]
#         self.threads_per_machine = [self.thread_load_calc.get_num_threads(machine_specs=machine_specs) for machine_specs in self.machines_specs]
#         self.workload_params = self.machine_load_calc.get_workload_params(machines_specs=self.machines_specs, threads_per_machine=self.threads_per_machine)
#         self.print_func_kwargs()

#     def viz_load_ratios(self) -> None:
#         if not self.workload_params: raise RuntimeError("func_kwargs_list is None. You need to run generate_standard_kwargs() first.")
#         import plottext
#         plt.simple_multiple_bar(names, [[machine_specs.cpu for machine_specs in self.machines_specs], [machine_specs.ram for machine_specs in self.machines_specs]], title="Resources per machine", labels=["#cpu threads", "memory size"])
#         plt.show()
#         print("")
#         plt.simple_bar(names, self.machine_load_calc.load_ratios, width=100, title=f"Load distribution for machines using criterion `{self.machine_load_calc.load_criterion}`")
#         plt.show()

#         # Capture load ratios as string
#         buffer = io.StringIO()
#         from rich import inspect
#         Console(file=buffer, width=75).print(inspect(dict(zip(names, L((np.array(self.machine_load_calc.load_ratios) * 100).round(1)).apply(lambda x: f"{int(x)}%"))), value=False, docs=False, dunder=False, sort=False))
#         tmp = buffer.getvalue()
#         assert isinstance(tmp, str)
#         self.machine_load_calc.load_ratios_repr = tmp
#         print(self.machine_load_calc.load_ratios_repr)
#         # self.workload_params.
#         print("\n")

#     def submit(self) -> None:
#         if not self.workload_params: raise RuntimeError("You need to generate standard kwargs first.")
#         for idx, (a_workload_params, an_ssh) in enumerate(zip(self.workload_params, self.sshz)):
#             desc = self.description + f"\nLoad Ratios on machines:\n{self.machine_load_calc.load_ratios_repr}"
#             # if self.remote_machine_kwargs is not None:
#             config = self.remote_machine_kwargs
#             config.__dict__.update(dict(description=desc, job_id=self.job_id + f"_{idx}", base_dir=self.root_dir, workload_params=a_workload_params, ssh_obj=an_ssh))
#             # else: config = RemoteMachineConfig(description=desc, job_id=self.job_id + f"_{idx}", base_dir=self.root_dir.as_posix(), workload_params=a_workload_params, ssh_obj=an_ssh)
#             m = RemoteMachine(func=self.func, func_kwargs=self.func_kwargs, config=config)
#             m.generate_scripts()
#             m.submit()
#             self.machines.append(m)
#         try: self.save()
#         except Exception as re:
#             print(re)
#             print("Couldn't pickle cluster object")
#         # self.print_commands()

#     def open_mux(self, machines_per_tab: int = 1, window_number: Optional[int] = None):
#         self.machines_per_tab = machines_per_tab
#         self.window_number = window_number if window_number is not None else 0  # randstr(length=3, lower=False, upper=False)
#         cmd = f"wt -w {self.window_number} "
#         for idx, m in enumerate(self.machines):

#             sub_cmd = m.get_session_manager().get_new_session_ssh_command(ssh=m.ssh, sess_name=m.job_params.session_name)
#             if idx == 0: cmd += f""" new-tab --title '{str(m.ssh.hostname) + str(idx)}' pwsh -Command "{sub_cmd}" `;"""  # avoid new tabs despite being even index
#             elif idx % self.machines_per_tab == 0: cmd += f""" new-tab --title {str(m.ssh.hostname) + str(idx)} pwsh -Command "{sub_cmd}" `;"""
#             else: cmd += f""" split-pane --horizontal --size {1 / self.machines_per_tab} pwsh -Command "{sub_cmd}" `;"""

#         print("Terminal launch command:\n", cmd)
#         if cmd.endswith("`;"): cmd = cmd[:-2]
#         Terminal().run_async(*cmd.replace("`;", ";").split(" "))  # `; only for powershell, cmd is okay for ; as it is not a special character
#         rm_last = self.machines[-1]
#         rm_last.get_session_manager().asssert_session_started(ssh=rm_last.ssh, sess_name=rm_last.job_params.session_name)

#     def fire(self, machines_per_tab: int = 1, window_number: Optional[int] = None, run: bool = False):
#         self.open_mux(machines_per_tab=machines_per_tab, window_number=window_number)
#         for m in self.machines:
#             m.fire(run=run, open_console=False)

#     def run(self, run: bool = False, machines_per_tab: int = 1, window_number: Optional[int] = None):
#         self.generate_standard_kwargs()
#         self.viz_load_ratios()
#         print(self)
#         self.submit()
#         self.fire(run=run, machines_per_tab=machines_per_tab, window_number=window_number)
#         self.save()
#         return self

#     def check_job_status(self) -> None: L(self.machines).apply(lambda machine: machine.check_job_status())
#     def download_results(self):
#         if self.results_downloaded:
#             print(f"All results downloaded to {self.root_dir} 🤗")
#             return True
#         for idx, a_m in enumerate(self.machines):
#             _ = idx
#             if a_m.results_path is None:
#                 print(f"Results are not ready for machine {a_m}.")
#                 print("Try to run `.check_job_status()` to check if the job is done and obtain results path.")
#                 continue
#             # results_folder = PathExtended(a_m.results_path).expanduser()
#             if a_m.results_downloaded is False:
#                 print("\n")
#                 console.rule(f"Downloading results from {a_m}")
#                 print("\n")
#                 a_m.download_results(target=None)  # TODO another way of resolve multiple machines issue is to create a directory at downlaod_results time.
#         if L(self.machines).results_downloaded.to_numpy().sum() == len(self.machines):
#             print(f"All results downloaded to {self.root_dir} 🤗")
#             self.results_downloaded = True


# if __name__ == '__main__':
#     pass
