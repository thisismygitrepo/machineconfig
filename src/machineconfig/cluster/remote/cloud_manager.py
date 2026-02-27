

import getpass
import platform
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from rich.console import Console

from machineconfig.utils.io import save_json, read_ini, read_json
from machineconfig.utils.source_of_truth import DEFAULTS_PATH
from machineconfig.cluster.remote.models import JOB_STATUS, LogEntry


LOCK_EXPIRY_SECONDS = 3600
SERVER_INTERVAL_SECONDS = 300
NUM_CLAIM_CHECKS = 3
INTER_CHECK_INTERVAL_SECONDS = 15


def _format_table_markdown(data: list[dict[str, object]]) -> str:
    if not data:
        return ""
    all_keys: set[str] = set()
    for row in data:
        all_keys.update(row.keys())
    keys = sorted(all_keys)
    header = "|" + "|".join(f" {k} " for k in keys) + "|"
    separator = "|" + "|".join(" --- " for _ in keys) + "|"
    rows: list[str] = []
    for row in data:
        vals = [f" {row.get(k, '') or ''} " for k in keys]
        rows.append("|" + "|".join(vals) + "|")
    return "\n".join([header, separator] + rows)


def _this_machine() -> str:
    return f"{getpass.getuser()}@{platform.node()}"


class CloudManager:
    base_path: Path = Path.home() / "tmp_results/remote_machines/cloud"

    def __init__(self, max_jobs: int, cloud: str | None, reset_local: bool) -> None:
        if reset_local:
            print("Resetting local cloud cache.")
            import shutil
            expanded = self.base_path.expanduser()
            if expanded.exists():
                shutil.rmtree(expanded)
        status_root = self.base_path.expanduser() / "workers" / _this_machine()
        status_root.mkdir(parents=True, exist_ok=True)
        self.status_root = status_root
        self.max_jobs = max_jobs
        if cloud is None:
            self.cloud = str(read_ini(DEFAULTS_PATH)["general"]["rclone_config_name"])
        else:
            self.cloud = cloud
        self.lock_claimed = False
        self.running_jobs: list[Any] = []
        self.console = Console()

    def read_log(self) -> dict[JOB_STATUS, list[dict[str, object]]]:
        if not self.lock_claimed:
            self.claim_lock(first_call=True)
        path = self.base_path.expanduser() / "logs.json"
        if not path.exists():
            log: dict[JOB_STATUS, list[dict[str, object]]] = {"queued": [], "running": [], "completed": [], "failed": []}
            path.parent.mkdir(parents=True, exist_ok=True)
            save_json(obj=log, path=path, indent=2, verbose=False)
            return log
        return read_json(path)

    def write_log(self, log: dict[JOB_STATUS, list[dict[str, object]]]) -> None:
        if not self.lock_claimed:
            self.claim_lock(first_call=True)
        save_json(obj=log, path=self.base_path.expanduser() / "logs.json", indent=2, verbose=False)

    def claim_lock(self, first_call: bool) -> None:
        if first_call:
            print("Claiming lock ...")
        machine = _this_machine()
        path = self.base_path.expanduser()
        path.mkdir(parents=True, exist_ok=True)
        lock_path = path / "lock.txt"
        _sync_from_cloud(self.cloud, lock_path)
        if not lock_path.exists():
            lock_path.write_text(machine, encoding="utf-8")
            _sync_to_cloud(self.cloud, lock_path)
            return self.claim_lock(first_call=False)
        lock_owner = lock_path.read_text(encoding="utf-8").strip()
        if lock_owner and lock_owner != machine:
            age = datetime.now() - datetime.fromtimestamp(lock_path.stat().st_mtime)
            if age.total_seconds() > LOCK_EXPIRY_SECONDS:
                print(f"Lock held by `{lock_owner}` for >{LOCK_EXPIRY_SECONDS}s. Resetting.")
                self.reset_lock()
                return self.claim_lock(first_call=False)
            wait = int(random.random() * 30)
            print(f"Lock held by `{lock_owner}`. Sleeping {wait}s.")
            time.sleep(wait)
            return self.claim_lock(first_call=False)
        if lock_owner == machine:
            print("Lock already held by this machine.")
        else:
            print("No lock claims, claiming ...")
        lock_path.write_text(machine, encoding="utf-8")
        _sync_to_cloud(self.cloud, lock_path)
        for check in range(1, NUM_CLAIM_CHECKS):
            time.sleep(INTER_CHECK_INTERVAL_SECONDS)
            _sync_from_cloud(self.cloud, lock_path)
            current_owner = lock_path.read_text(encoding="utf-8").strip()
            if current_owner != machine:
                print(f"Lock challenged by `{current_owner}`. Retrying.")
                time.sleep(INTER_CHECK_INTERVAL_SECONDS)
                return self.claim_lock(first_call=False)
            print(f"Lock claim check {check}/{NUM_CLAIM_CHECKS} passed.")
        _sync_dir_from_cloud(self.cloud, self.base_path.expanduser())
        print("Lock claimed.")
        self.lock_claimed = True

    def release_lock(self) -> None:
        if not self.lock_claimed:
            print("Lock not claimed, nothing to release.")
            return
        lock_path = self.base_path.expanduser() / "lock.txt"
        _sync_from_cloud(self.cloud, lock_path)
        if lock_path.exists():
            current = lock_path.read_text(encoding="utf-8").strip()
            if current != _this_machine():
                raise RuntimeError(f"Lock held by `{current}`, not this machine. Cannot release.")
        lock_path.write_text("", encoding="utf-8")
        _sync_dir_to_cloud(self.cloud, self.base_path.expanduser())
        self.lock_claimed = False
        print("Lock released.")

    def reset_lock(self) -> None:
        lock_path = self.base_path.expanduser() / "lock.txt"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("", encoding="utf-8")
        _sync_to_cloud(self.cloud, lock_path)

    def reset_cloud(self, unsafe: bool) -> None:
        print("Resetting cloud.")
        if not unsafe:
            self.claim_lock(first_call=True)
        import shutil
        expanded = self.base_path.expanduser()
        if expanded.exists():
            shutil.rmtree(expanded)
        expanded.mkdir(parents=True, exist_ok=True)
        _sync_dir_to_cloud(self.cloud, expanded)
        self.release_lock()

    def start_jobs_if_possible(self) -> None:
        from machineconfig.cluster.remote.remote_machine import RemoteMachine
        if len(self.running_jobs) >= self.max_jobs:
            print(f"At capacity ({len(self.running_jobs)}/{self.max_jobs})")
            return
        log = self.read_log()
        if not log["queued"]:
            print("No queued jobs.")
            return
        idx = 0
        while len(self.running_jobs) < self.max_jobs and idx < len(log["queued"]):
            entry = LogEntry.from_dict(log["queued"][idx])
            job_path = self.base_path.expanduser() / f"jobs/{entry.name}"
            rm_json = job_path / "data/remote_machine.json"
            if not rm_json.exists():
                idx += 1
                continue
            rm: RemoteMachine = RemoteMachine.from_job_dir(job_path)
            if rm.config.allowed_remotes is not None and _this_machine() not in rm.config.allowed_remotes:
                print(f"Job `{entry.name}` not allowed on this machine.")
                idx += 1
                continue
            pid, _cmd = rm.fire(run=True)
            entry.pid = pid
            entry.run_machine = _this_machine()
            entry.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry.session_name = rm.job_params.session_name
            log["queued"] = [j for j in log["queued"] if j.get("name") != entry.name]
            log["running"].append(entry.__dict__)
            self.running_jobs.append(rm)
            self.write_log(log=log)

    def get_running_jobs_statuses(self) -> None:
        to_remove: list[str] = []
        for rm in self.running_jobs:
            status = rm.file_manager.get_job_status(session_name=rm.job_params.session_name, tab_name=rm.job_params.tab_name)
            if status in ("completed", "failed"):
                log = self.read_log()
                entry_data = next((j for j in log["running"] if j.get("name") == rm.config.job_id), None)
                if entry_data:
                    entry = LogEntry.from_dict(entry_data)
                    entry.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log[status].append(entry.__dict__)
                    log["running"] = [j for j in log["running"] if j.get("name") != rm.config.job_id]
                self.write_log(log=log)
                to_remove.append(rm.config.job_id)
        self.running_jobs = [rm for rm in self.running_jobs if rm.config.job_id not in to_remove]
        running_ids = [rm.config.job_id for rm in self.running_jobs]
        save_json(obj=running_ids, path=self.status_root / "running_jobs.json", indent=2, verbose=False)

    def clean_interrupted_jobs(self, return_to_queue: bool) -> None:
        from machineconfig.cluster.remote.remote_machine import RemoteMachine
        machine = _this_machine()
        log = self.read_log()
        dirt: list[str] = []
        for job_data in log["running"]:
            entry = LogEntry.from_dict(job_data)
            if entry.run_machine != machine:
                continue
            job_path = self.base_path.expanduser() / f"jobs/{entry.name}"
            rm_json = job_path / "data/remote_machine.json"
            if not rm_json.exists():
                continue
            rm: RemoteMachine = RemoteMachine.from_job_dir(job_path)
            status = rm.file_manager.get_job_status(session_name=rm.job_params.session_name, tab_name=rm.job_params.tab_name)
            if status == "running":
                self.running_jobs.append(rm)
            else:
                entry.pid = None
                entry.cmd = None
                entry.start_time = None
                entry.end_time = None
                entry.run_machine = None
                entry.session_name = None
                entry.note += f"| Interrupted on `{machine}`"
                dirt.append(entry.name)
                target = "queued" if return_to_queue else "failed"
                log[target].append(entry.__dict__)
                print(f"Job `{entry.name}` moved to {target}.")
        log["running"] = [j for j in log["running"] if j.get("name") not in dirt]
        self.write_log(log=log)

    def serve(self) -> None:
        from machineconfig.utils.scheduler import Scheduler
        self.clean_interrupted_jobs(return_to_queue=True)

        def routine(_sched: object) -> None:
            self.start_jobs_if_possible()
            self.get_running_jobs_statuses()
            self.release_lock()

        sched = Scheduler(routine=routine, wait_ms=SERVER_INTERVAL_SECONDS * 1000, logger=_null_logger())
        sched.run()

    def run_monitor(self) -> None:
        from machineconfig.utils.scheduler import Scheduler

        def routine(_sched: object) -> None:
            lock_path = self.base_path.expanduser() / "lock.txt"
            _sync_from_cloud(self.cloud, lock_path)
            lock_owner = lock_path.read_text(encoding="utf-8").strip() if lock_path.exists() else "None"
            self.console.print(f"Lock: {lock_owner}")
            log_path = self.base_path.expanduser() / "logs.json"
            _sync_from_cloud(self.cloud, log_path)
            if log_path.exists():
                log: dict[str, list[dict[str, object]]] = read_json(log_path)
                for status_name, entries in log.items():
                    self.console.rule(f"{status_name} ({len(entries)})")
                    display = entries[-10:]
                    if display:
                        print(_format_table_markdown(display))
            workers_dir = self.base_path.expanduser() / "workers"
            if workers_dir.exists():
                report = _prepare_servers_report(workers_dir)
                print("\nWorkers:")
                print(_format_table_markdown(report))

        sched = Scheduler(routine=routine, wait_ms=300_000, logger=_null_logger())
        sched.run()


def _prepare_servers_report(workers_root: Path) -> list[dict[str, object]]:
    report: list[dict[str, object]] = []
    if not workers_root.exists():
        return report
    for worker_dir in workers_root.iterdir():
        running_json = worker_dir / "running_jobs.json"
        if running_json.exists():
            jobs: list[str] = read_json(running_json)
            mod_time = datetime.fromtimestamp(running_json.stat().st_mtime)
            last_update = datetime.now() - mod_time
        else:
            jobs = []
            last_update = timedelta(0)
        report.append({"machine": worker_dir.name, "running_jobs": len(jobs), "last_update": str(last_update)})
    return report


def _sync_from_cloud(cloud: str, path: Path) -> None:
    import subprocess
    rel = _rel2home(path)
    subprocess.run(["rclone", "copy", f"{cloud}:{rel}", str(path.parent)], capture_output=True, check=False)


def _sync_to_cloud(cloud: str, path: Path) -> None:
    import subprocess
    rel = _rel2home(path)
    subprocess.run(["rclone", "copy", str(path), f"{cloud}:{Path(rel).parent}"], capture_output=True, check=False)


def _sync_dir_from_cloud(cloud: str, directory: Path) -> None:
    import subprocess
    rel = _rel2home(directory)
    subprocess.run(["rclone", "sync", f"{cloud}:{rel}", str(directory)], capture_output=True, check=False)


def _sync_dir_to_cloud(cloud: str, directory: Path) -> None:
    import subprocess
    rel = _rel2home(directory)
    subprocess.run(["rclone", "sync", str(directory), f"{cloud}:{rel}"], capture_output=True, check=False)


def _rel2home(path: Path) -> str:
    try:
        return str(path.expanduser().resolve().relative_to(Path.home()))
    except ValueError:
        return str(path)


class _NullLogger:
    def trace(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def success(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def debug(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def info(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def error(self, __message: str, *args: Any, **kwargs: Any) -> None: pass
    def critical(self, __message: str, *args: Any, **kwargs: Any) -> None: pass


def _null_logger() -> _NullLogger:
    return _NullLogger()
