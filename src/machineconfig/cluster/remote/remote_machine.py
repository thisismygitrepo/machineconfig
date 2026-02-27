from __future__ import annotations

from typing import Callable
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from machineconfig.utils.accessories import randstr
from machineconfig.utils.io import save_pickle
from machineconfig.utils.ssh import SSH
from machineconfig.cluster.remote.models import RemoteMachineConfig, EmailParams, WorkloadParams, LogEntry
from machineconfig.cluster.remote.job_params import JobParams
from machineconfig.cluster.remote.file_manager import FileManager
from machineconfig.cluster.remote.execution_script import render_execution_script
from machineconfig.cluster.remote.notification import render_notification_block
from machineconfig.cluster.remote.data_transfer import transfer_sftp, transfer_cloud

console = Console()


class RemoteMachine:
    def __init__(self, func: str | Callable[..., object], config: RemoteMachineConfig, func_kwargs: dict[str, object] | None, data: list[str] | None) -> None:
        self.config = config
        if callable(func) and not isinstance(func, (str, Path)):
            self.job_params = JobParams.from_callable(func)
        else:
            self.job_params = JobParams.from_script(str(func))
        if config.workload_params is not None and func_kwargs is not None:
            if "workload_params" in func_kwargs:
                raise ValueError("workload_params provided in both config and func_kwargs")
        self.kwargs: dict[str, object] = func_kwargs or {}
        self.data: list[str] = data if data is not None else []
        self.ssh: SSH | None = None
        self.file_manager = FileManager(job_id=config.job_id, remote_machine_type="Linux", lock_resources=config.lock_resources, max_simultaneous_jobs=config.max_simultaneous_jobs, base=config.base_dir)
        self.submitted: bool = False
        self.scripts_generated: bool = False
        self.results_downloaded: bool = False
        self.results_path: Path | None = None

    def __repr__(self) -> str:
        ssh_repr = self.ssh.get_remote_repr(add_machine=True) if self.ssh else (self.config.ssh_host or "local")
        return f"RemoteMachine({ssh_repr})"

    def __getstate__(self) -> dict[str, object]:
        state = self.__dict__.copy()
        state["ssh"] = None  # SSH connections are not picklable
        return state

    def __setstate__(self, state: dict[str, object]) -> None:
        self.__dict__ = state

    def _ensure_ssh(self) -> SSH:
        if self.ssh is None:
            if self.config.ssh_host is None:
                raise ValueError("ssh_host must be set in config to connect to a remote machine")
            self.ssh = SSH.from_config_file(host=self.config.ssh_host)
        return self.ssh

    def generate_scripts(self) -> None:
        console.rule(f"Generating scripts for job `{self.file_manager.job_id}` @ {self!r}")
        self.job_params.ssh_repr = repr(self.ssh) if self.ssh else ""
        self.job_params.ssh_repr_remote = self.ssh.get_remote_repr() if self.ssh else ""
        self.job_params.description = self.config.description
        self.job_params.file_manager_path = str(self.file_manager.file_manager_path)
        self.job_params.session_name = "TS-" + randstr(noun=True)
        self.job_params.tab_name = f"job-{self.file_manager.job_id}"

        execution_line = self.job_params.get_execution_line(parallelize=self.config.parallelize, workload_params=self.config.workload_params, wrap_in_try_except=self.config.wrap_in_try_except)

        notification_block = ""
        if self.config.notify_upon_completion:
            assert self.config.email_config_name is not None
            assert self.config.to_email is not None
            email_params = EmailParams(
                addressee=self.ssh.get_local_repr(add_machine=True) if self.ssh else "local",
                speaker=self.ssh.get_remote_repr(add_machine=True) if self.ssh else "local",
                ssh_conn_str=self.ssh.get_remote_repr(add_machine=False) if self.ssh else "",
                executed_obj=f"{self.job_params.repo_path_rh}/{self.job_params.file_path_r}",
                file_manager_path=str(self.file_manager.file_manager_path),
                to_email=self.config.to_email,
                email_config_name=self.config.email_config_name,
            )
            notification_block = render_notification_block(email_params)

        # Save params pickle first so the template can reference it
        params_pickle_path = self.file_manager.job_root / "data/job_params.pkl"
        params_pickle_path.parent.mkdir(parents=True, exist_ok=True)
        save_pickle(obj=self.job_params, path=params_pickle_path, verbose=False)

        py_script = render_execution_script(
            params_pickle_path=str(params_pickle_path),
            file_manager_pickle_path=str(self.file_manager.file_manager_path),
            execution_line=execution_line,
            notification_block=notification_block,
        )

        shell_script = _build_shell_script(self.job_params, self.config, self.file_manager)

        # Write shell script
        shell_path = self.file_manager.shell_script_path.expanduser()
        shell_path.parent.mkdir(parents=True, exist_ok=True)
        shell_path.write_text(shell_script, encoding="utf-8")

        # Write python script
        py_path = self.file_manager.py_script_path.expanduser()
        py_path.parent.mkdir(parents=True, exist_ok=True)
        py_path.write_text(py_script, encoding="utf-8")

        # Save supporting data
        save_pickle(obj=self.kwargs, path=self.file_manager.kwargs_path.expanduser(), verbose=False)
        save_pickle(obj=self.file_manager.__getstate__(), path=self.file_manager.file_manager_path.expanduser(), verbose=False)
        save_pickle(obj=self.config, path=self.file_manager.remote_machine_config_path.expanduser(), verbose=False)
        save_pickle(obj=self, path=self.file_manager.remote_machine_path.expanduser(), verbose=False)

        log_dir = self.file_manager.execution_log_dir.expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "status.txt").write_text("queued", encoding="utf-8")
        self.scripts_generated = True

    def show_scripts(self) -> None:
        shell_text = self.file_manager.shell_script_path.expanduser().read_text(encoding="utf-8")
        py_text = self.file_manager.py_script_path.expanduser().read_text(encoding="utf-8")
        console.print(Panel(Syntax(shell_text, lexer="sh", theme="monokai", line_numbers=True), title="Shell Script"))
        console.print(Panel(Syntax(py_text, lexer="python", theme="monokai", line_numbers=True), title="Python Script"))

    def submit(self) -> None:
        console.rule("Submitting job")
        if self.config.ssh_host is not None:
            ssh = self._ensure_ssh()
            if self.config.transfer_method == "sftp":
                transfer_sftp(ssh=ssh, config=self.config, job_params=self.job_params, file_manager=self.file_manager, data=self.data)
            elif self.config.transfer_method == "cloud":
                transfer_cloud(ssh=ssh, config=self.config, job_params=self.job_params, file_manager=self.file_manager, data=self.data)
            else:
                raise ValueError(f"Unknown transfer_method: {self.config.transfer_method}")
        self.submitted = True

    def fire(self, run: bool) -> tuple[int, str]:
        if not self.submitted:
            raise RuntimeError("Job not submitted yet")
        console.rule(f"Firing job `{self.config.job_id}`")
        cmd = self.file_manager.get_fire_command()
        if self.config.ssh_host is not None:
            ssh = self._ensure_ssh()
            response = ssh.run_shell_cmd_on_remote(command=cmd, verbose_output=True, description=f"fire job {self.config.job_id}", strict_stderr=False, strict_return_code=False)
            return 0, response.op
        else:
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout

    def run(self, run: bool, show_scripts: bool) -> "RemoteMachine":
        self.generate_scripts()
        if show_scripts:
            self.show_scripts()
        self.submit()
        self.fire(run=run)
        return self

    def check_job_status(self) -> Path | None:
        if not self.submitted:
            print("Job not submitted yet.")
            return None
        if self.results_downloaded:
            print("Results already downloaded.")
            return None
        log_dir = self.file_manager.execution_log_dir.expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        if self.config.ssh_host is not None:
            ssh = self._ensure_ssh()
            try:
                ssh.copy_to_here(source=str(self.file_manager.execution_log_dir), target=None, compress_with_zip=True, recursive=True)
            except Exception:
                pass
        end_time_file = log_dir / "end_time.txt"
        if not end_time_file.exists():
            start_file = log_dir / "start_time.txt"
            if not start_file.exists():
                print(f"Job {self.config.job_id} still queued.")
            else:
                start_time = start_file.read_text(encoding="utf-8").strip()
                try:
                    elapsed = datetime.now() - datetime.fromisoformat(start_time)
                    msg = f"Job `{self.config.job_id}` running since {start_time} ({elapsed})"
                except ValueError:
                    msg = f"Job `{self.config.job_id}` running since {start_time}"
                console.print(Panel(msg, title="Job Status", border_style="bold red"))
            return None
        results_folder_file = log_dir / "results_folder_path.txt"
        results_folder = results_folder_file.read_text(encoding="utf-8").strip()
        console.rule("Job Completed")
        print(f"Results: {results_folder}")
        self.results_path = Path(results_folder)
        return self.results_path

    def download_results(self, target: str | None) -> "RemoteMachine":
        if self.results_path is None:
            raise RuntimeError("Results path unknown. Check job status first.")
        if self.results_downloaded:
            print(f"Results already downloaded: {self.results_path}")
            return self
        if self.config.ssh_host is not None:
            ssh = self._ensure_ssh()
            ssh.copy_to_here(source=str(self.results_path), target=target, compress_with_zip=True, recursive=True)
        self.results_downloaded = True
        return self

    def delete_remote_results(self) -> "RemoteMachine":
        if self.results_path is None:
            print("Results path unknown.")
            return self
        if self.config.ssh_host is not None:
            ssh = self._ensure_ssh()
            ssh.run_shell_cmd_on_remote(command=f"rm -rf {self.results_path}", verbose_output=False, description="delete remote results", strict_stderr=False, strict_return_code=False)
        return self

    def submit_to_cloud(self, cm: object, split: int, reset_cloud: bool) -> list["RemoteMachine"]:
        from copy import deepcopy
        from machineconfig.cluster.remote.cloud_manager import CloudManager
        import getpass
        import platform as plat

        if not isinstance(cm, CloudManager):
            raise TypeError("cm must be a CloudManager instance")
        if self.config.transfer_method != "cloud":
            raise ValueError("CloudManager requires transfer_method='cloud'")
        if self.config.launch_method != "cloud_manager":
            raise ValueError("CloudManager requires launch_method='cloud_manager'")
        if reset_cloud:
            cm.reset_cloud(unsafe=False)
        cm.claim_lock(first_call=True)

        self.config.base_dir = str(CloudManager.base_path / "jobs")
        self.file_manager.base_dir = Path(self.config.base_dir)

        wl = WorkloadParams.default().split_to_jobs(jobs=split)
        rms: list[RemoteMachine] = []
        new_entries: list[LogEntry] = []
        for idx, a_wl in enumerate(wl):
            rm = deepcopy(self)
            rm.config.job_id = f"{rm.config.job_id}-{idx + 1}-{split}"
            rm.config.workload_params = a_wl if len(wl) > 1 else None
            rm.file_manager.job_root = self.file_manager.base_dir / rm.config.job_id
            rm.file_manager.job_id = rm.config.job_id
            rm.submitted = True
            rm.generate_scripts()
            rms.append(rm)
            new_entries.append(LogEntry(
                name=rm.config.job_id, submission_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                start_time=None, end_time=None, run_machine=None,
                source_machine=f"{getpass.getuser()}@{plat.node()}",
                note="", pid=None, cmd="", session_name="",
            ))

        log = cm.read_log()
        for entry in new_entries:
            log["queued"].append(entry.__dict__)
        cm.write_log(log=log)
        cm.release_lock()
        return rms


def _build_shell_script(job_params: JobParams, config: RemoteMachineConfig, file_manager: FileManager) -> str:
    lines: list[str] = ['echo "=== SHELL START ==="']
    lines.append(f"cd {job_params.repo_path_rh}")
    if config.update_repo:
        lines.append("git pull")
    if config.install_repo:
        lines.append("pip install -e .")
    lines.append('echo "=== SHELL END ==="')
    lines.append(f'echo "Starting job {config.job_id}"')
    py_rel = file_manager.py_script_path
    try:
        py_rel_str = str(py_rel.relative_to(Path.home()))
    except ValueError:
        py_rel_str = str(py_rel)
    lines.append("cd ~")
    if config.interactive:
        lines.append(f"python -i ./{py_rel_str}")
    else:
        lines.append(f"python ./{py_rel_str}")
    return "\n".join(lines) + "\n"
