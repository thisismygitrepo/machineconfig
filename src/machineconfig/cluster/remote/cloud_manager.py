# from machineconfig.utils.utils2 import read_ini
# from machineconfig.utils.io_save import save_pickle

# from machineconfig.cluster.loader_runner import JOB_STATUS, LogEntry
# from typing import Optional, Any, NoReturn
# from rich.console import Console
# import pickle
# import time
# import getpass
# import random
# import platform
# from datetime import datetime, timedelta


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


# class CloudManager:
#     base_path = PathExtended("~/tmp_results/remote_machines/cloud")
#     server_interval_sec: int = 60 * 5
#     num_claim_checks: int = 3
#     inter_check_interval_sec: int = 15
#     def __init__(self, max_jobs: int, cloud: Optional[str] = None, reset_local: bool = False) -> None:
#         if reset_local:
#             print("☠️ Resetting local cloud cache ☠️. Locally created / completed jobs not yet synced will not make it to the cloud.")
#             PathExtended(self.base_path).expanduser().delete(sure=True)
#         status_root_path = self.base_path.expanduser().joinpath("workers", f"{getpass.getuser()}@{platform.node()}")
#         status_root_path.mkdir(parents=True, exist_ok=True)
#         self.status_root: P = status_root_path
#         self.max_jobs: int = max_jobs
#         if cloud is None:
#             from machineconfig.utils.utils import DEFAULTS_PATH
#             self.cloud = read_ini(DEFAULTS_PATH)['general']['rclone_config_name']
#         else: self.cloud = cloud
#         self.lock_claimed = False
#         from machineconfig.cluster.remote_machine import RemoteMachine
#         self.running_jobs: list[RemoteMachine] = []
#         self.console = Console()

#     # =================== READ WRITE OF LOGS ===================
#     def read_log(self) -> dict[JOB_STATUS, list[dict[str, Any]]]:
#         # assert self.claim_lock, f"method should never be called without claiming the lock first. This is a cloud-wide file."
#         if not self.lock_claimed: self.claim_lock()
#         path = self.base_path.joinpath("logs.pkl").expanduser()
#         if not path.exists():
#             log: dict[JOB_STATUS, list[dict[str, Any]]] = {}
#             log['queued'] = []
#             log['running'] = []
#             log['completed'] = []
#             log['failed'] = []
#             path.parent.mkdir(parents=True, exist_ok=True)
#             save_pickle(obj=log, path=path, verbose=False)
#             return log
#         return pickle.loads(path.read_bytes())
#     def write_log(self, log: dict[JOB_STATUS, list[dict[str, Any]]]) -> None:
#         # assert self.claim_lock, f"method should never be called without claiming the lock first. This is a cloud-wide file."
#         if not self.lock_claimed: self.claim_lock()
#         save_pickle(obj=log, path=self.base_path.joinpath("logs.pkl").expanduser(), verbose=False)

#     # =================== CLOUD MONITORING ===================
#     def fetch_cloud_live(self):
#         remote = CloudManager.base_path
#         localpath = PathExtended.tmp().joinpath("tmp_dirs/cloud_manager_live")
#         localpath.mkdir(parents=True, exist_ok=True)
#         alternative_base = localpath.delete(sure=True).from_cloud(cloud=self.cloud, remotepath=remote.get_remote_path(root="myhome", rel2home=True), verbose=False)
#         return alternative_base
#     @staticmethod
#     def prepare_servers_report(cloud_root: PathExtended) -> list[dict[str, Any]]:
#         from machineconfig.cluster.remote_machine import RemoteMachine
#         workers_root = [p for p in cloud_root.joinpath("workers").iterdir()]
#         res: dict[str, list[RemoteMachine]] = {}
#         times: dict[str, timedelta] = {}
#         for a_worker in workers_root:
#             running_jobs = a_worker.joinpath("running_jobs.pkl")
#             file_mod_time = datetime.fromtimestamp(running_jobs.stat().st_mtime) if running_jobs.exists() else datetime.min
#             times[a_worker.name] = datetime.now() - file_mod_time
#             res[a_worker.name] = pickle.loads(running_jobs.read_bytes()) if running_jobs.exists() else []

#         # Create list of dictionaries instead of DataFrame
#         servers_report = []
#         for machine in res.keys():
#             servers_report.append({
#                 "machine": machine,
#                 "#RJobs": len(res[machine]),
#                 "LastUpdate": times[machine]
#             })
#         return servers_report
#     def run_monitor(self):
#         """Without syncing, bring the latest from the cloud to random local path (not the default path, as that would require the lock)"""
#         from rich import print as pprint
#         def routine(sched: Any):
#             _ = sched
#             alternative_base = self.fetch_cloud_live()
#             assert alternative_base is not None
#             lock_path = alternative_base.expanduser().joinpath("lock.txt")
#             if lock_path.exists(): lock_owner: str = lock_path.read_text(encoding="utf-8")
#             else: lock_owner = "None"
#             self.console.print(f"🔒 Lock is held by: {lock_owner}")
#             self.console.print("🧾 Log File:")
#             log_path = alternative_base.joinpath("logs.pkl")
#             if log_path.exists(): log: dict[JOB_STATUS, list[dict[str, Any]]] = pickle.loads(log_path.read_bytes())
#             else:
#                 self.console.print("Log file doesn't exist! 🫤 must be that cloud is getting purged or something 🤔 ")
#                 log = {}
#             for item_name, item_list in log.items():
#                 self.console.rule(f"{item_name} Jobs (Latest {'10' if len(item_list) > 10 else len(item_list)} / {len(item_list)})")
#                 print()  # empty line after the rule helps keeping the rendering clean in the terminal while zooming in and out.

#                 # Add duration calculation for non-queued items
#                 display_items = []
#                 for item in item_list:
#                     display_item = item.copy()
#                     if item_name != "queued" and "start_time" in item and item["start_time"]:
#                         try:
#                             if item_name == "running":
#                                 end_time = datetime.now()
#                             else:
#                                 end_time = datetime.fromisoformat(item["end_time"]) if item.get("end_time") else datetime.now()
#                             start_time = datetime.fromisoformat(item["start_time"])
#                             display_item["duration"] = end_time - start_time
#                         except Exception:
#                             display_item["duration"] = "unknown"
#                     display_items.append(display_item)

#                 # Filter columns based on item type
#                 excluded_cols = {"cmd", "note"}
#                 if item_name == "queued": excluded_cols.update({"pid", "start_time", "end_time", "run_machine"})
#                 if item_name == "running": excluded_cols.update({"submission_time", "source_machine", "end_time"})
#                 if item_name == "completed": excluded_cols.update({"submission_time", "source_machine", "start_time", "pid"})
#                 if item_name == "failed": excluded_cols.update({"submission_time", "source_machine", "start_time"})

#                 # Filter items and take last 10
#                 filtered_items = []
#                 for item in display_items[-10:]:
#                     filtered_item = {k: v for k, v in item.items() if k not in excluded_cols}
#                     filtered_items.append(filtered_item)

#                 if filtered_items:
#                     pprint(format_table_markdown(filtered_items))
#                 pprint("\n\n")
#             print("👷 Workers:")
#             servers_report = self.prepare_servers_report(cloud_root=alternative_base)
#             pprint(format_table_markdown(servers_report))
#         sched = Scheduler(routine=routine, wait="5m")
#         sched.run()

#     # ================== CLEARNING METHODS ===================
#     def clean_interrupted_jobs_mess(self, return_to_queue: bool = True):
#         """Clean jobs that failed but in logs show running by looking at the pid.
#         If you want to do the same for remote machines, you will need to do it manually using `rerun_jobs`"""
#         assert len(self.running_jobs) == 0, "method should never be called while there are running jobs. This can only be called at the beginning of the run."
#         from machineconfig.cluster.remote_machine import RemoteMachine
#         this_machine = f"{getpass.getuser()}@{platform.node()}"
#         log = self.read_log()
#         # servers_report = self.prepare_servers_report(cloud_root=CloudManager.base_path.expanduser())
#         dirt: list[str] = []
#         for job_data in log["running"]:
#             entry = LogEntry.from_dict(job_data)
#             if entry.run_machine != this_machine: continue
#             a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
#             rm: RemoteMachine = pickle.loads(a_job_path.joinpath("data/remote_machine.Machine.pkl").read_bytes())
#             status = rm.file_manager.get_job_status(session_name=rm.job_params.session_name, tab_name=rm.job_params.tab_name)
#             if status == "running":
#                 print(f"Job `{entry.name}` is still running, added to running jobs.")
#                 self.running_jobs.append(rm)
#             else:
#                 entry.pid = None
#                 entry.cmd = None
#                 entry.start_time = None
#                 entry.end_time = None
#                 entry.run_machine = None
#                 entry.session_name = None
#                 rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
#                 rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
#                 entry.note += f"| Job was interrupted by a crash of the machine `{this_machine}`."
#                 dirt.append(entry.name)
#                 print(f"Job `{entry.name}` is not running, removing it from log of running jobs.")
#                 if return_to_queue:
#                     log["queued"].append(entry.__dict__)
#                     print(f"Job `{entry.name}` is not running, returning it to the queue.")
#                 else:
#                     log["failed"].append(entry.__dict__)
#                     print(f"Job `{entry.name}` is not running, moving it to failed jobs.")
#         # Remove entries that are in dirt list
#         log["running"] = [job for job in log["running"] if job.get("name") not in dirt]
#         self.write_log(log=log)
#     def clean_failed_jobs_mess(self):
#         """If you want to do it for remote machine, use `rerun_jobs` (manual selection)"""
#         print("⚠️ Cleaning failed jobs mess for this machine ⚠️")
#         from machineconfig.cluster.remote_machine import RemoteMachine
#         log = self.read_log()
#         for job_data in log["failed"]:
#             entry = LogEntry.from_dict(job_data)
#             a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
#             rm: RemoteMachine = pickle.loads(a_job_path.joinpath("data/remote_machine.Machine.pkl").read_bytes())
#             entry.note += f"| Job failed @ {entry.run_machine}"
#             entry.pid = None
#             entry.cmd = None
#             entry.start_time = None
#             entry.end_time = None
#             entry.run_machine = None
#             entry.session_name = None
#             rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
#             rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
#             print(f"Job `{entry.name}` is not running, removing it from log of running jobs.")
#             log["queued"].append(entry.__dict__)
#             print(f"Job `{entry.name}` is not running, returning it to the queue.")
#         log["failed"] = []
#         self.write_log(log=log)
#         self.release_lock()
#     def rerun_jobs(self):
#         """This method involves manual selection but has all-files scope (failed and running) and can be used for both local and remote machines.
#         The reason it is not automated for remotes is because even though the server might have failed, the processes therein might be running, so there is no automated way to tell."""
#         log = self.read_log()
#         jobs_all: list[str] = [p.name for p in self.base_path.expanduser().joinpath("jobs").iterdir()]
#         jobs_selected = choose_from_options(options=jobs_all, msg="Select Jobs to Redo", multi=True, tv=True)
#         for a_job in jobs_selected:
#             # find in which log list does this job live:
#             found_log_type = None
#             found_entry_data = None
#             for log_type, log_list in log.items():
#                 for job_data in log_list:
#                     if job_data.get("name") == a_job:
#                         found_log_type = log_type
#                         found_entry_data = job_data
#                         break
#                 if found_log_type:
#                     break

#             if not found_log_type:
#                 raise ValueError(f"Job `{a_job}` is not found in any of the log lists.")

#             if found_entry_data is None:
#                 raise ValueError(f"Job `{a_job}` has no entry data.")

#             entry = LogEntry.from_dict(found_entry_data)
#             a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
#             entry.note += f"| Job failed @ {entry.run_machine}"
#             entry.pid = None
#             entry.cmd = None
#             entry.start_time = None
#             entry.end_time = None
#             entry.run_machine = None
#             entry.session_name = None
#             rm: RemoteMachine = pickle.loads(a_job_path.joinpath("data/remote_machine.Machine.pkl").read_bytes())
#             rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
#             rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
#             log["queued"].append(entry.__dict__)
#             # Remove from original log type
#             log[found_log_type] = [job for job in log[found_log_type] if job.get("name") != a_job]
#             print(f"Job `{entry.name}` was removed from {found_log_type} and added to the queue in order to be re-run.")
#         self.write_log(log=log)
#         self.release_lock()

#     def serve(self):
#         self.clean_interrupted_jobs_mess()
#         def routine(sched: Any):
#             _ = sched
#             self.start_jobs_if_possible()
#             self.get_running_jobs_statuses()
#             self.release_lock()
#         sched = Scheduler(routine=routine, wait=f"{self.server_interval_sec}s")
#         return sched.run()

#     def get_running_jobs_statuses(self):
#         """This is the only authority responsible for moving jobs from running df to failed df or completed df."""
#         jobs_ids_to_be_removed_from_running: list[str] = []
#         for a_rm in self.running_jobs:
#             status = a_rm.file_manager.get_job_status(session_name=a_rm.job_params.session_name, tab_name=a_rm.job_params.tab_name)
#             if status == "running": pass
#             elif status == "completed" or status == "failed":
#                 job_name = a_rm.config.job_id
#                 log = self.read_log()

#                 # Find the entry in running jobs
#                 entry_data = None
#                 for job_data in log["running"]:
#                     if job_data.get("name") == job_name:
#                         entry_data = job_data
#                         break

#                 if entry_data:
#                     entry = LogEntry.from_dict(entry_data)
#                     entry.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                     log[status].append(entry.__dict__)
#                     # Remove from running
#                     log["running"] = [job for job in log["running"] if job.get("name") != job_name]
#                 self.write_log(log=log)
#                 # self.running_jobs.remove(a_rm)
#                 jobs_ids_to_be_removed_from_running.append(a_rm.config.job_id)
#             elif status == "queued": raise RuntimeError("I thought I'm working strictly with running jobs, and I encountered unexpected a job with `queued` status.")
#             else: raise ValueError(f"I receieved a status that I don't know how to handle `{status}`")
#         self.running_jobs = [a_rm for a_rm in self.running_jobs if a_rm.config.job_id not in jobs_ids_to_be_removed_from_running]
#         save_pickle(obj=self.running_jobs, path=self.status_root.joinpath("running_jobs.pkl"), verbose=False)
#         self.status_root.to_cloud(cloud=self.cloud, rel2home=True, verbose=False)  # no need for lock as this writes to a folder specific to this machine.
#     def start_jobs_if_possible(self):
#         """This is the only authority responsible for moving jobs from queue df to running df."""
#         if len(self.running_jobs) == self.max_jobs:
#             print(f"⚠️ No more capacity to run more jobs ({len(self.running_jobs)} / {self.max_jobs=})")
#             return
#         from machineconfig.cluster.remote_machine import RemoteMachine
#         log = self.read_log()  # ask for the log file.
#         if len(log["queued"]) == 0:
#             print("No queued jobs found.")
#             return None
#         idx: int = 0
#         while len(self.running_jobs) < self.max_jobs:
#             if idx >= len(log["queued"]):
#                 break  # looked at all jobs in the queue

#             queue_entry = LogEntry.from_dict(log["queued"][idx])
#             a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{queue_entry.name}")
#             rm: RemoteMachine = pickle.loads(a_job_path.joinpath("data/remote_machine.Machine.pkl").read_bytes())
#             if rm.config.allowed_remotes is not None and f"{getpass.getuser()}@{platform.node()}" not in rm.config.allowed_remotes:
#                 print(f"Job `{queue_entry.name}` is not allowed to run on this machine. Skipping ...")
#                 idx += 1
#                 continue  # look at the next job in the queue.

#             pid, _process_cmd = rm.fire(run=True)
#             queue_entry.pid = pid
#             # queue_entry.cmd = process_cmd
#             queue_entry.run_machine = f"{getpass.getuser()}@{platform.node()}"
#             queue_entry.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             queue_entry.session_name = rm.job_params.session_name

#             # Remove from queued and add to running
#             log["queued"] = [job for job in log["queued"] if job.get("name") != queue_entry.name]
#             log["running"].append(queue_entry.__dict__)
#             self.running_jobs.append(rm)
#             self.write_log(log=log)
#         return None

#     def reset_cloud(self, unsafe: bool = False):
#         print("☠️ Resetting cloud server ☠️")
#         if not unsafe: self.claim_lock()  # it is unsafe to ignore the lock since other workers thinnk they own the lock and will push their data and overwrite the reset. Do so only when knowing that other
#         base_path = CloudManager.base_path.expanduser().delete(sure=True)
#         base_path.mkdir(parents=True, exist_ok=True)
#         base_path.sync_to_cloud(cloud=self.cloud, rel2home=True, sync_up=True, verbose=True, transfers=100)
#         self.release_lock()
#     def reset_lock(self):
#         base_path = CloudManager.base_path.expanduser()
#         base_path.mkdir(parents=True, exist_ok=True)
#         base_path.joinpath("lock.txt").write_text("").to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#     @staticmethod
#     def run_clean_trial():
#         self = CloudManager(max_jobs=1)
#         base_path = self.base_path.expanduser().delete(sure=True)
#         base_path.mkdir(parents=True, exist_ok=True)
#         base_path.sync_to_cloud(cloud=self.cloud, rel2home=True, sync_up=True, transfers=20)
#         from machineconfig.cluster.templates.run_remote import run_on_cloud
#         run_on_cloud()
#         self.serve()
#     def claim_lock(self, first_call: bool = True) -> None:
#         """
#         Note: If the parameters of the class are messed with, there is no gaurantee of zero collision by this method.
#         It takes at least inter_check_interval_sec * num_claims_check to claim the lock.
#         """
#         if first_call: print("Claiming lock 🔒 ...")
#         this_machine = f"{getpass.getuser()}@{platform.node()}"
#         path = CloudManager.base_path.expanduser()
#         path.mkdir(parents=True, exist_ok=True)
#         lock_path = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#         if lock_path is None:
#             print("Lock doesn't exist on remote, uploading for the first time.")
#             path.joinpath("lock.txt").write_text(this_machine).to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#             return self.claim_lock(first_call=False)

#         locking_machine = lock_path.read_text(encoding="utf-8")
#         if locking_machine != "" and locking_machine != this_machine:
#             lock_mod_time = datetime.fromtimestamp(lock_path.stat().st_mtime)
#             if (datetime.now() - lock_mod_time).total_seconds() > 3600:
#                 print(f"⚠️ Lock was claimed by `{locking_machine}` for more than an hour. Something wrong happened there. Resetting the lock!")
#                 self.reset_lock()
#                 return self.claim_lock(first_call=False)
#             print(f"CloudManager: Lock already claimed by `{locking_machine}`. 🤷‍♂️")
#             wait = int(random.random() * 30)
#             print(f"💤 sleeping for {wait} seconds and trying again.")
#             time.sleep(wait)
#             return self.claim_lock(first_call=False)

#         if locking_machine == this_machine: print("Lock already claimed by this machine. 🤭")
#         elif locking_machine == "": print("No claims on lock, claiming it ... 🙂")
#         else: raise ValueError("Unexpected value of lock_data at this point of code.")

#         path.joinpath("lock.txt").write_text(this_machine).to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#         counter: int = 1
#         while counter < self.num_claim_checks:
#             lock_path_tmp = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#             assert lock_path_tmp is not None
#             lock_data_tmp = lock_path_tmp.read_text(encoding="utf-8")
#             if lock_data_tmp != this_machine:
#                 print(f"CloudManager: Lock already claimed by `{lock_data_tmp}`. 🤷‍♂️")
#                 print(f"sleeping for {self.inter_check_interval_sec} seconds and trying again.")
#                 time.sleep(self.inter_check_interval_sec)
#                 return self.claim_lock(first_call=False)
#             counter += 1
#             print(f"‼️ Claim laid, waiting for 10 seconds and checking if this is challenged: #{counter}-{self.num_claim_checks} ❓")
#             time.sleep(10)
#         CloudManager.base_path.expanduser().sync_to_cloud(cloud=self.cloud, rel2home=True, verbose=False, sync_down=True)
#         print("✅ Lock Claimed 🔒")
#         self.lock_claimed = True

#     def release_lock(self):
#         if not self.lock_claimed:
#             print("⚠️ Lock is not claimed, nothing to release.")
#             return
#         print("Releasing Lock")
#         path = CloudManager.base_path.expanduser()
#         path.mkdir(parents=True, exist_ok=True)
#         lock_path = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#         if lock_path is None:
#             print("Lock doesn't exist on remote, uploading for the first time.")
#             path.joinpath("lock.txt").write_text("").to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#             self.lock_claimed = False
#             return NoReturn
#         data = lock_path.read_text(encoding="utf-8")
#         this_machine = f"{getpass.getuser()}@{platform.node()}"
#         if data != this_machine:
#             raise ValueError(f"CloudManager: Lock already claimed by `{data}`. 🤷‍♂️ Can't release a lock not owned! This shouldn't happen. Consider increasing trails before confirming the claim.")
#             # self.lock_claimed = False
#         path.joinpath("lock.txt").write_text("")
#         CloudManager.base_path.expanduser().sync_to_cloud(cloud=self.cloud, rel2home=True, verbose=False, sync_up=True)  # .to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
#         self.lock_claimed = False
#         return NoReturn
