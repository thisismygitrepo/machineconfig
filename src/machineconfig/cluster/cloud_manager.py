

import pandas as pd

from crocodile.file_management import P, Save, Read
from crocodile.meta import Scheduler
from machineconfig.cluster.loader_runner import JOB_STATUS, LogEntry
from typing import Optional, Any, NoReturn
from rich.console import Console
import time
from dataclasses import fields
import getpass
import random
import platform


class CloudManager:
    base_path = P("~/tmp_results/remote_machines/cloud")
    server_interval_sec: int = 60 * 5
    num_claim_checks: int = 3
    inter_check_interval_sec: int = 15
    def __init__(self, max_jobs: int, cloud: Optional[str] = None, reset_local: bool = False) -> None:
        if reset_local:
            print("☠️ Resetting local cloud cache ☠️. Locally created / completed jobs not yet synced will not make it to the cloud.")
            P(self.base_path).expanduser().delete(sure=True)
        self.status_root: P = self.base_path.expanduser().joinpath("workers", f"{getpass.getuser()}@{platform.node()}").create()
        self.max_jobs: int = max_jobs
        if cloud is None:
            from machineconfig.utils.utils import DEFAULTS_PATH
            self.cloud = Read.ini(DEFAULTS_PATH)['general']['rclone_config_name']
        else: self.cloud = cloud
        self.lock_claimed = False
        from machineconfig.cluster.remote_machine import RemoteMachine
        self.running_jobs: list[RemoteMachine] = []
        self.console = Console()

    # =================== READ WRITE OF LOGS ===================
    def read_log(self) -> dict[JOB_STATUS, 'pd.DataFrame']:
        # assert self.claim_lock, f"method should never be called without claiming the lock first. This is a cloud-wide file."
        if not self.lock_claimed: self.claim_lock()
        path = self.base_path.joinpath("logs.pkl").expanduser()
        if not path.exists():
            cols = [a_field.name for a_field in fields(LogEntry)]
            log: dict[JOB_STATUS, 'pd.DataFrame'] = {}
            log['queued'] = pd.DataFrame(columns=cols)
            log['running'] = pd.DataFrame(columns=cols)
            log['completed'] = pd.DataFrame(columns=cols)
            log['failed'] = pd.DataFrame(columns=cols)
            Save.pickle(obj=log, path=path.create(parents_only=True), verbose=False)
            return log
        return Read.pickle(path=path)
    def write_log(self, log: dict[JOB_STATUS, 'pd.DataFrame']):
        # assert self.claim_lock, f"method should never be called without claiming the lock first. This is a cloud-wide file."
        if not self.lock_claimed: self.claim_lock()
        Save.pickle(obj=log, path=self.base_path.joinpath("logs.pkl").expanduser(), verbose=False)
        return NoReturn

    # =================== CLOUD MONITORING ===================
    def fetch_cloud_live(self):
        remote = CloudManager.base_path
        localpath = P.tmp().joinpath("tmp_dirs/cloud_manager_live").create()
        alternative_base = localpath.delete(sure=True).from_cloud(cloud=self.cloud, remotepath=remote.get_remote_path(root="myhome", rel2home=True), verbose=False)
        return alternative_base
    @staticmethod
    def prepare_servers_report(cloud_root: P):
        from machineconfig.cluster.remote_machine import RemoteMachine
        workers_root = cloud_root.joinpath("workers").search("*")
        res: dict[str, list[RemoteMachine]] = {}
        times: dict[str, pd.Timedelta] = {}
        for a_worker in workers_root:
            running_jobs = a_worker.joinpath("running_jobs.pkl")
            times[a_worker.name] = pd.Timestamp.now() - pd.to_datetime(running_jobs.time("m"))
            res[a_worker.name] = Read.pickle(path=running_jobs) if running_jobs.exists() else []
        servers_report = pd.DataFrame({"machine": list(res.keys()), "#RJobs": [len(x) for x in res.values()], "LastUpdate": list(times.values())})
        return servers_report
    def run_monitor(self):
        """Without syncing, bring the latest from the cloud to random local path (not the default path, as that would require the lock)"""
        from rich import print as pprint
        def routine(sched: Any):
            _ = sched
            alternative_base = self.fetch_cloud_live()
            assert alternative_base is not None
            lock_path = alternative_base.expanduser().joinpath("lock.txt")
            if lock_path.exists(): lock_owner: str = lock_path.read_text()
            else: lock_owner = "None"
            self.console.print(f"🔒 Lock is held by: {lock_owner}")
            self.console.print("🧾 Log File:")
            log_path = alternative_base.joinpath("logs.pkl")
            if log_path.exists(): log: dict[JOB_STATUS, 'pd.DataFrame'] = Read.pickle(path=log_path)
            else:
                self.console.print("Log file doesn't exist! 🫤 must be that cloud is getting purged or something 🤔 ")
                log = {}
            for item_name, item_df in log.items():
                self.console.rule(f"{item_name} DataFrame (Latest {'10' if len(item_df) > 10 else len(item_df)} / {len(item_df)})")
                print()  # empty line after the rule helps keeping the rendering clean in the terminal while zooming in and out.
                if item_name != "queued":
                    t2 = pd.to_datetime(item_df["end_time"]) if item_name != "running" else pd.Series([pd.Timestamp.now()] * len(item_df))
                    if len(t2) == 0 and len(item_df) == 0: pass  # the subtraction below gives an error if both are empty. TypeError: cannot subtract DatetimeArray from ndarray
                    else: item_df["duration"] = t2 - pd.to_datetime(item_df["start_time"])

                cols = item_df.columns
                cols = [a_col for a_col in cols if a_col not in {"cmd", "note"}]
                if item_name == "queued": cols = [a_col for a_col in cols if a_col not in {"pid", "start_time", "end_time", "run_machine"}]
                if item_name == "running": cols = [a_col for a_col in cols if a_col not in {"submission_time", "source_machine", "end_time"}]
                if item_name == "completed": cols = [a_col for a_col in cols if a_col not in {"submission_time", "source_machine", "start_time", "pid"}]
                if item_name == "failed": cols = [a_col for a_col in cols if a_col not in {"submission_time", "source_machine", "start_time"}]
                pprint(item_df[cols][-10:].to_markdown())
                pprint("\n\n")
            print("👷 Workers:")
            servers_report = self.prepare_servers_report(cloud_root=alternative_base)
            pprint(servers_report.to_markdown())
        sched = Scheduler(routine=routine, wait="5m")
        sched.run()

    # ================== CLEARNING METHODS ===================
    def clean_interrupted_jobs_mess(self, return_to_queue: bool = True):
        """Clean jobs that failed but in logs show running by looking at the pid.
        If you want to do the same for remote machines, you will need to do it manually using `rerun_jobs`"""
        assert len(self.running_jobs) == 0, "method should never be called while there are running jobs. This can only be called at the beginning of the run."
        from machineconfig.cluster.remote_machine import RemoteMachine
        this_machine = f"{getpass.getuser()}@{platform.node()}"
        log = self.read_log()
        # servers_report = self.prepare_servers_report(cloud_root=CloudManager.base_path.expanduser())
        dirt: list[str] = []
        for _idx, row in log["running"].iterrows():
            entry = LogEntry.from_dict(row.to_dict())
            if entry.run_machine != this_machine: continue
            a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
            rm: RemoteMachine = Read.pickle(path=a_job_path.joinpath("data/remote_machine.Machine.pkl"))
            status = rm.file_manager.get_job_status(session_name=rm.job_params.session_name, tab_name=rm.job_params.tab_name)
            if status == "running":
                print(f"Job `{entry.name}` is still running, added to running jobs.")
                self.running_jobs.append(rm)
            else:
                entry.pid = None
                entry.cmd = None
                entry.start_time = None
                entry.end_time = None
                entry.run_machine = None
                entry.session_name = None
                rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
                rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
                entry.note += f"| Job was interrupted by a crash of the machine `{this_machine}`."
                dirt.append(entry.name)
                print(f"Job `{entry.name}` is not running, removing it from log of running jobs.")
                if return_to_queue:
                    log["queued"] = pd.concat([log["queued"], pd.DataFrame([entry.__dict__])], ignore_index=True)
                    print(f"Job `{entry.name}` is not running, returning it to the queue.")
                else:
                    log["failed"] = pd.concat([log["failed"], pd.DataFrame([entry.__dict__])], ignore_index=True)
                    print(f"Job `{entry.name}` is not running, moving it to failed jobs.")
        log["running"] = log["running"][~log["running"]["name"].isin(dirt)]
        self.write_log(log=log)
    def clean_failed_jobs_mess(self):
        """If you want to do it for remote machine, use `rerun_jobs` (manual selection)"""
        print("⚠️ Cleaning failed jobs mess for this machine ⚠️")
        from machineconfig.cluster.remote_machine import RemoteMachine
        log = self.read_log()
        for _idx, row in log["failed"].iterrows():
            entry = LogEntry.from_dict(row.to_dict())
            a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
            rm: RemoteMachine = Read.pickle(path=a_job_path.joinpath("data/remote_machine.Machine.pkl"))
            entry.note += f"| Job failed @ {entry.run_machine}"
            entry.pid = None
            entry.cmd = None
            entry.start_time = None
            entry.end_time = None
            entry.run_machine = None
            entry.session_name = None
            rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
            rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
            print(f"Job `{entry.name}` is not running, removing it from log of running jobs.")
            log["queued"] = pd.concat([log["queued"], pd.DataFrame([entry.__dict__])], ignore_index=True)
            print(f"Job `{entry.name}` is not running, returning it to the queue.")
        log["failed"] = pd.DataFrame(columns=log["failed"].columns)
        self.write_log(log=log)
        self.release_lock()
    def rerun_jobs(self):
        """This method involves manual selection but has all-files scope (failed and running) and can be used for both local and remote machines.
        The reason it is not automated for remotes is because even though the server might have failed, the processes therein might be running, so there is no automated way to tell."""
        log = self.read_log()
        from machineconfig.cluster.remote_machine import RemoteMachine
        from machineconfig.utils.utils import display_options
        jobs_all: list[str] = self.base_path.expanduser().joinpath("jobs").search("*").apply(lambda x: x.name).list
        jobs_selected = display_options(options=jobs_all, msg="Select Jobs to Redo", multi=True, fzf=True)
        for a_job in jobs_selected:
            # find in which dataframe does this job lives:
            for log_type, log_df in log.items():
                if a_job in log_df["name"].values: break
            else: raise ValueError(f"Job `{a_job}` is not found in any of the log dataframes.")
            entry = LogEntry.from_dict(log_df[log_df["name"] == a_job].iloc[0].to_dict())
            a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{entry.name}")
            entry.note += f"| Job failed @ {entry.run_machine}"
            entry.pid = None
            entry.cmd = None
            entry.start_time = None
            entry.end_time = None
            entry.run_machine = None
            entry.session_name = None
            rm: RemoteMachine = Read.pickle(path=a_job_path.joinpath("data/remote_machine.Machine.pkl"))
            rm.file_manager.execution_log_dir.expanduser().joinpath("status.txt").delete(sure=True)
            rm.file_manager.execution_log_dir.expanduser().joinpath("pid.txt").delete(sure=True)
            log["queued"] = pd.concat([log["queued"], pd.DataFrame([entry.__dict__])], ignore_index=True)
            log[log_type] = log[log_type][log[log_type]["name"] != a_job]
            print(f"Job `{entry.name}` was removed from {log_type} and added to the queue in order to be re-run.")
        self.write_log(log=log)
        self.release_lock()

    def serve(self):
        self.clean_interrupted_jobs_mess()
        def routine(sched: Any):
            _ = sched
            self.start_jobs_if_possible()
            self.get_running_jobs_statuses()
            self.release_lock()
        sched = Scheduler(routine=routine, wait=f"{self.server_interval_sec}s")
        return sched.run()

    def get_running_jobs_statuses(self):
        """This is the only authority responsible for moving jobs from running df to failed df or completed df."""
        jobs_ids_to_be_removed_from_running: list[str] = []
        for a_rm in self.running_jobs:
            status = a_rm.file_manager.get_job_status(session_name=a_rm.job_params.session_name, tab_name=a_rm.job_params.tab_name)
            if status == "running": pass
            elif status == "completed" or status == "failed":
                job_name = a_rm.config.job_id
                log = self.read_log()
                df_to_add = log[status]
                df_to_take = log["running"]
                entry = LogEntry.from_dict(df_to_take[df_to_take["name"] == job_name].iloc[0].to_dict())
                entry.end_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                df_to_add = pd.concat([df_to_add, pd.DataFrame([entry.__dict__])], ignore_index=True)
                df_to_take = df_to_take[df_to_take["name"] != job_name]
                log[status] = df_to_add
                log["running"] = df_to_take
                self.write_log(log=log)
                # self.running_jobs.remove(a_rm)
                jobs_ids_to_be_removed_from_running.append(a_rm.config.job_id)
            elif status == "queued": raise RuntimeError("I thought I'm working strictly with running jobs, and I encountered unexpected a job with `queued` status.")
            else: raise ValueError(f"I receieved a status that I don't know how to handle `{status}`")
        self.running_jobs = [a_rm for a_rm in self.running_jobs if a_rm.config.job_id not in jobs_ids_to_be_removed_from_running]
        Save.pickle(obj=self.running_jobs, path=self.status_root.joinpath("running_jobs.pkl"), verbose=False)
        self.status_root.to_cloud(cloud=self.cloud, rel2home=True, verbose=False)  # no need for lock as this writes to a folder specific to this machine.
    def start_jobs_if_possible(self):
        """This is the only authority responsible for moving jobs from queue df to running df."""
        if len(self.running_jobs) == self.max_jobs:
            print(f"⚠️ No more capacity to run more jobs ({len(self.running_jobs)} / {self.max_jobs=})")
            return
        from machineconfig.cluster.remote_machine import RemoteMachine
        log = self.read_log()  # ask for the log file.
        if len(log["queued"]) == 0:
            print("No queued jobs found.")
            return None
        idx: int = 0
        while len(self.running_jobs) < self.max_jobs:
            queue_entry = LogEntry.from_dict(log["queued"].iloc[idx].to_dict())
            a_job_path = CloudManager.base_path.expanduser().joinpath(f"jobs/{queue_entry.name}")
            rm: RemoteMachine = Read.pickle(path=a_job_path.joinpath("data/remote_machine.Machine.pkl"))
            if rm.config.allowed_remotes is not None and f"{getpass.getuser()}@{platform.node()}" not in rm.config.allowed_remotes:
                print(f"Job `{queue_entry.name}` is not allowed to run on this machine. Skipping ...")
                idx += 1
                if idx >= len(log["queued"]):
                    break  # looked at all jobs in the queue and none is allowed to run on this machine.
                continue  # look at the next job in the queue.
            pid, _process_cmd = rm.fire(run=True)
            queue_entry.pid = pid
            # queue_entry.cmd = process_cmd
            queue_entry.run_machine = f"{getpass.getuser()}@{platform.node()}"
            queue_entry.start_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            queue_entry.session_name = rm.job_params.session_name
            log["queued"] = log["queued"][log["queued"]["name"] != queue_entry.name]
            # log["queued"] = log["queued"].iloc[1:] if len(log["queued"]) > 0 else pd.DataFrame(columns=log["queued"].column)
            log["running"] = pd.concat([log["running"], pd.DataFrame([queue_entry.__dict__])], ignore_index=True)
            self.running_jobs.append(rm)
            self.write_log(log=log)
        return None

    def reset_cloud(self, unsafe: bool = False):
        print("☠️ Resetting cloud server ☠️")
        if not unsafe: self.claim_lock()  # it is unsafe to ignore the lock since other workers thinnk they own the lock and will push their data and overwrite the reset. Do so only when knowing that other
        CloudManager.base_path.expanduser().delete(sure=True).create().sync_to_cloud(cloud=self.cloud, rel2home=True, sync_up=True, verbose=True, transfers=100)
        self.release_lock()
    def reset_lock(self): CloudManager.base_path.expanduser().create().joinpath("lock.txt").write_text("").to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
    @staticmethod
    def run_clean_trial():
        self = CloudManager(max_jobs=1)
        self.base_path.expanduser().delete(sure=True).create().sync_to_cloud(cloud=self.cloud, rel2home=True, sync_up=True, transfers=20)
        from machineconfig.cluster.templates.run_remote import run_on_cloud
        run_on_cloud()
        self.serve()
    def claim_lock(self, first_call: bool = True):
        """
        Note: If the parameters of the class are messed with, there is no gaurantee of zero collision by this method.
        It takes at least inter_check_interval_sec * num_claims_check to claim the lock.
        """
        if first_call: print("Claiming lock 🔒 ...")
        this_machine = f"{getpass.getuser()}@{platform.node()}"
        path = CloudManager.base_path.expanduser().create()
        lock_path = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
        if lock_path is None:
            print("Lock doesn't exist on remote, uploading for the first time.")
            path.joinpath("lock.txt").write_text(this_machine).to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
            return self.claim_lock(first_call=False)

        locking_machine = lock_path.read_text()
        if locking_machine != "" and locking_machine != this_machine:
            if (pd.Timestamp.now() - lock_path.time("m")).total_seconds() > 3600:
                print(f"⚠️ Lock was claimed by `{locking_machine}` for more than an hour. Something wrong happened there. Resetting the lock!")
                self.reset_lock()
                return self.claim_lock(first_call=False)
            print(f"CloudManager: Lock already claimed by `{locking_machine}`. 🤷‍♂️")
            wait = int(random.random() * 30)
            print(f"💤 sleeping for {wait} seconds and trying again.")
            time.sleep(wait)
            return self.claim_lock(first_call=False)

        if locking_machine == this_machine: print("Lock already claimed by this machine. 🤭")
        elif locking_machine == "": print("No claims on lock, claiming it ... 🙂")
        else: raise ValueError("Unexpected value of lock_data at this point of code.")

        path.joinpath("lock.txt").write_text(this_machine).to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
        counter: int = 1
        while counter < self.num_claim_checks:
            lock_path_tmp = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
            assert lock_path_tmp is not None
            lock_data_tmp = lock_path_tmp.read_text()
            if lock_data_tmp != this_machine:
                print(f"CloudManager: Lock already claimed by `{lock_data_tmp}`. 🤷‍♂️")
                print(f"sleeping for {self.inter_check_interval_sec} seconds and trying again.")
                time.sleep(self.inter_check_interval_sec)
                return self.claim_lock(first_call=False)
            counter += 1
            print(f"‼️ Claim laid, waiting for 10 seconds and checking if this is challenged: #{counter}-{self.num_claim_checks} ❓")
            time.sleep(10)
        CloudManager.base_path.expanduser().sync_to_cloud(cloud=self.cloud, rel2home=True, verbose=False, sync_down=True)
        print("✅ Lock Claimed 🔒")
        self.lock_claimed = True

    def release_lock(self):
        if not self.lock_claimed:
            print("⚠️ Lock is not claimed, nothing to release.")
            return
        print("Releasing Lock")
        path = CloudManager.base_path.expanduser().create()
        lock_path = path.joinpath("lock.txt").from_cloud(cloud=self.cloud, rel2home=True, verbose=False)
        if lock_path is None:
            print("Lock doesn't exist on remote, uploading for the first time.")
            path.joinpath("lock.txt").write_text("").to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
            self.lock_claimed = False
            return NoReturn
        data = lock_path.read_text()
        this_machine = f"{getpass.getuser()}@{platform.node()}"
        if data != this_machine:
            raise ValueError(f"CloudManager: Lock already claimed by `{data}`. 🤷‍♂️ Can't release a lock not owned! This shouldn't happen. Consider increasing trails before confirming the claim.")
            # self.lock_claimed = False
        path.joinpath("lock.txt").write_text("")
        CloudManager.base_path.expanduser().sync_to_cloud(cloud=self.cloud, rel2home=True, verbose=False, sync_up=True)  # .to_cloud(cloud=self.cloud, rel2home=True, verbose=False)
        self.lock_claimed = False
        return NoReturn
