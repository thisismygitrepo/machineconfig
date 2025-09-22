# from rich.console import Console
# from machineconfig.utils.utils2 import pprint
# from datetime import datetime


# from machineconfig.utils.io_save import save_pickle
# from machineconfig.cluster.loader_runner import JOB_STATUS, LAUNCH_METHOD, JobStatus

# from typing import Union, Any
# import time
# import os
# import platform

# console = Console()


# class FileManager:
#     running_path          = PathExtended("~/tmp_results/remote_machines/file_manager/running_jobs.pkl")
#     queue_path            = PathExtended("~/tmp_results/remote_machines/file_manager/queued_jobs.pkl")
#     history_path          = PathExtended("~/tmp_results/remote_machines/file_manager/history_jobs.pkl")
#     shell_script_path_log = PathExtended("~/tmp_results/remote_machines/file_manager/last_cluster_script.txt")
#     default_base          = PathExtended("~/tmp_results/remote_machines/jobs")
#     @staticmethod
#     def from_pickle(path: Union[str, P]):
#         fm = FileManager(job_id='1', remote_machine_type='Windows', lock_resources=True, max_simulataneous_jobs=1, base=None)
#         fm.__setstate__(dict(PathExtended(path).expanduser().readit()))
#         return fm
#     def __getstate__(self): return self.__dict__
#     def __setstate__(self, state: dict[str, Any]): self.__dict__ = state
#     def __init__(self, job_id: str, remote_machine_type: MACHINE, lock_resources: bool, max_simulataneous_jobs: int = 1, base: Union[str, P, None] = None):
#         """Log files to track execution process:
#         * A text file that cluster deletes at the begining then write to at the end of each job.
#         * pickle of Machine and clusters objects.
#         """
#         # EVERYTHING MUST REMAIN IN RELATIVE PATHS
#         self.remote_machine_type = remote_machine_type
#         self.job_id = job_id
#         self.max_simulataneous_jobs = max_simulataneous_jobs
#         self.lock_resources = lock_resources

#         self.submission_time = datetime.now()

#         self.base_dir = PathExtended(base).collapseuser() if bool(base) else FileManager.default_base
#         status: JOB_STATUS
#         status = 'queued'
#         self.job_root = self.base_dir.joinpath(f"{status}/{self.job_id}")
#     @property
#     def py_script_path(self): return self.job_root.joinpath("python/cluster_wrap.py")
#     @property
#     def cloud_download_py_script_path(self): return self.job_root.joinpath("python/download_data.py")
#     @property
#     def shell_script_path(self): return self.job_root.joinpath("shell/cluster_script" + {"Windows": ".ps1", "Linux": ".sh"}[self.remote_machine_type])  # noqa: E501
#     @property
#     def kwargs_path(self): return self.job_root.joinpath("data/func_kwargs.pkl")
#     @property
#     def file_manager_path(self): return self.job_root.joinpath("data/file_manager.pkl")
#     @property
#     def remote_machine_path(self): return self.job_root.joinpath("data/remote_machine.Machine.pkl")
#     @property
#     def remote_machine_config_path(self): return self.job_root.joinpath("data/remote_machine_config.pkl")
#     @property
#     def execution_log_dir(self): return self.job_root.joinpath("logs")
#     def get_fire_command(self, launch_method: LAUNCH_METHOD):
#         _ = launch_method
#         script_path = self.shell_script_path.expanduser()
#         # if launch_method == "remotely": pass  # shell_script is already repared for target machine.
#         # else:
#         if platform.system() == "Windows" and script_path.name.endswith(".sh"):
#             tmp = script_path.with_suffix(".ps1")
#             tmp.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8", newline=None)
#             script_path = tmp
#         if platform.system() == "Linux" and script_path.name.endswith(".ps1"):
#             tmp = script_path.with_suffix(".sh")
#             tmp.write_text(script_path.read_text(encoding="utf-8"), encoding="utf-8", newline='\n')
#             script_path = tmp
#         return f". {script_path}"
#     def get_job_status(self, session_name: str, tab_name: str) -> JOB_STATUS:
#         pid_path = self.execution_log_dir.expanduser().joinpath("pid.txt")
#         tmp = self.execution_log_dir.expanduser().joinpath("status.txt").read_text(encoding="utf-8")
#         status: JOB_STATUS = tmp  # type: ignore
#         if status == "running":
#             if not pid_path.exists():
#                 print(f"Something wrong happened to job `{self.job_id}`. Its status log file says `{status}`, but pid_path doesn't exists. Moving to failed.")
#                 status = 'failed'
#                 self.execution_log_dir.expanduser().joinpath("status.txt").write_text(status)
#                 return status
#             pid: int = int(pid_path.read_text(encoding="utf-8").rstrip())
#             import psutil
#             try: proc = psutil.Process(pid=pid)
#             except psutil.NoSuchProcess:
#                 print(f"Something wrong happened to job `{self.job_id}`.. Its status log file says `{status}`, but its declared `{pid=}` is dead. Moving to failed.")
#                 status = 'failed'
#                 self.execution_log_dir.expanduser().joinpath("status.txt").write_text(status)
#                 return status
#             command = " ".join(proc.cmdline())
#             if self.job_id not in command:
#                 print(f"Something wrong happened to job `{self.job_id}`. Its status log file says `{status}` but the `{pid=}` declared seem to belong to a different process as indicated by the firing command `{command=}`. Moving to failed.")
#                 status = 'failed'
#                 self.execution_log_dir.expanduser().joinpath("status.txt").write_text(status)
#                 return status
#             print(f"Job `{self.job_id}` is running with {pid=} & {session_name=} & {tab_name=}.")
#             return status
#         return status

#     def add_to_queue(self, job_status: JobStatus):
#         try:
#             queue_file: list[JobStatus] = self.queue_path.expanduser().readit()
#         except FileNotFoundError:
#             print("Queue file was deleted by the locking job, creating an empty one and saving it.")
#             queue_file = []
#             save_pickle(obj=queue_file, path=self.queue_path.expanduser())
#         job_ids = [job.job_id for job in queue_file]
#         if self.job_id not in job_ids:
#             print(f"Adding this job {self.job_id} to the queue and saving it. {len(queue_file)=}")
#             queue_file.append(job_status)
#             save_pickle(obj=queue_file, path=self.queue_path.expanduser())
#         return queue_file

#     def get_resources_unlocking(self):  # this one works at shell level in case python script failed.
#         return f"""
# rm {self.running_path.collapseuser().as_posix()}
# echo "Unlocked resources"
# """

#     def secure_resources(self):
#         if self.lock_resources is False: return True
#         this_job = JobStatus(job_id=self.job_id, pid=os.getpid(), submission_time=self.submission_time, start_time=None, status='locked')
#         sleep_time_mins = 10
#         lock_status = 'locked'
#         while lock_status == 'locked':

#             try: running_file: list[JobStatus] = self.running_path.expanduser().readit()
#             except FileNotFoundError:
#                 print("Running file was deleted by the locking job, making one.")
#                 running_file = []
#                 save_pickle(obj=running_file, path=self.running_path.expanduser())

#             queue_file = self.add_to_queue(job_status=this_job)

#             if len(running_file) < self.max_simulataneous_jobs:
#                 lock_status = 'unlocked'
#                 break

#             # --------------- Clearning up queue_file from dead processes -----------------
#             import psutil
#             next_job_in_queue = queue_file[0]  # only consider the first job in the queue
#             try: _ = psutil.Process(next_job_in_queue.pid)
#             except psutil.NoSuchProcess:
#                 print(f"Next job in queue {next_job_in_queue} has no associated process, removing it from the queue.")
#                 queue_file.pop(0)
#                 save_pickle(obj=queue_file, path=self.queue_path.expanduser())
#                 continue

#             # --------------- Clearning up running_file from dead processes -----------------
#             found_dead_process = False
#             assert len(running_file) > 0, "Running file is empty. This should not happen. There should be a break before this point."

#             for running_job in running_file:
#                 try: proc = psutil.Process(pid=running_job.pid)
#                 except psutil.NoSuchProcess:
#                     print(f"Locking process with pid {running_job.pid} is dead. Ignoring this lock file.")
#                     pprint(running_job.__dict__, "Ignored Lock File Details")
#                     running_file.remove(running_job)
#                     save_pickle(obj=running_file, path=self.running_path.expanduser())
#                     found_dead_process = True
#                     continue  # for for loop
#                 attrs_txt = ['status', 'memory_percent', 'exe', 'num_ctx_switches',
#                              'ppid', 'num_threads', 'pid', 'cpu_percent', 'create_time', 'nice',
#                              'name', 'cpu_affinity', 'cmdline', 'username', 'cwd']
#                 # if self.remote_machine_type == 'Windows': attrs_txt += ['num_handles']
#                 # environ, memory_maps, 'io_counters'
#                 attrs_objs = ['memory_info', 'memory_full_info', 'cpu_times', 'ionice', 'threads', 'open_files', 'connections']
#                 pprint(proc.as_dict(attrs=attrs_objs), f"Process holding the Lock (pid = {running_job.pid})")
#                 pprint(proc.as_dict(attrs=attrs_txt), f"Process holding the Lock (pid = {running_job.pid})")

#             if found_dead_process: continue  # repeat while loop logic.
#             running_job = running_file[0]  # arbitrary job in the running file.
#             assert running_job.start_time is not None, f"Running job {running_job} has no start time. This should not happen."

#             now = datetime.now()
#             this_specs = {"Submission time": this_job.submission_time, "Time now": now,
#                           "Time spent waiting in the queue so far 🛌": now - this_job.submission_time,
#                           f"Time consumed by locking job so far (job_id = {running_job.job_id}) so far ⏰": now - running_job.start_time}
#             pprint(this_specs, f"This Job `{this_job.job_id}` Details")
#             console.rule(title=f"Resources are locked by another job `{running_job.job_id}`. Sleeping for {sleep_time_mins} minutes. 😴", style="bold red", characters="-")
#             print("\n")
#             time.sleep(sleep_time_mins * 60)
#         self.write_lock_file(job_status=this_job)
#         console.print(f"Resources are locked by this job `{self.job_id}`. Process pid = {os.getpid()}.", highlight=True)

#     def write_lock_file(self, job_status: JobStatus):
#         job_status.start_time = datetime.now()
#         queue_path = self.queue_path.expanduser()
#         try: queue_file: list[JobStatus] = queue_path.readit()
#         except FileNotFoundError as fne: raise FileNotFoundError(f"Queue file {queue_path} does not exist. This method should not be called in the first place.") from fne

#         if job_status in queue_file: queue_file.remove(job_status)
#         print("Removed current job from waiting queue and added it to the running queue. Saving both files.")
#         save_pickle(obj=queue_file, path=queue_path)

#         running_path = self.running_path.expanduser()
#         try: running_file: list[JobStatus] = running_path.readit()
#         except FileNotFoundError as fne: raise FileNotFoundError(f"Queue file {running_path} does not exist. This method should not be called in the first place.") from fne

#         assert job_status not in running_file, f"Job status {job_status} is already in the running file. This should not happen."
#         assert len(running_file) < self.max_simulataneous_jobs, f"Number of running jobs ({len(running_file)}) is greater than the maximum allowed ({self.max_simulataneous_jobs}). This method should not be called in the first place."
#         running_file.append(job_status)
#         save_pickle(obj=running_file, path=running_path)

#     def unlock_resources(self):
#         if self.lock_resources is False: return True
#         running_file: list[JobStatus] = self.running_path.expanduser().readit()
#         for job_status in running_file:
#             if job_status.job_id == self.job_id:
#                 this_job = job_status
#                 break
#         else:
#             print(f"Job {self.job_id} is not in the running file. This should not happen. The file is corrupt.")
#             this_job = None
#         if this_job is not None:
#             running_file.remove(this_job)
#         console.print(f"Resources have been released by this job `{self.job_id}`. Saving new running file")
#         save_pickle(path=self.running_path.expanduser(), obj=running_file)
#         start_time_str = self.execution_log_dir.expanduser().joinpath("start_time.txt").readit()
#         start_time = datetime.fromisoformat(start_time_str)
#         end_time = datetime.now()
#         item = {"job_id": self.job_id, "start_time": start_time, "end_time": end_time, "submission_time": self.submission_time}
#         hist_file = self.history_path.expanduser()
#         if hist_file.exists(): hist = hist_file.readit()
#         else: hist = []
#         hist.append(item)
#         print(f"Saved history file to {hist_file} with {len(hist)} items.")
#         save_pickle(obj=hist, path=hist_file)
#         # this is further handled by the calling script in case this function failed.
