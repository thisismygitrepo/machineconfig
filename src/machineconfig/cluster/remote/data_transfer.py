

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from machineconfig.utils.ssh import SSH
    from machineconfig.cluster.remote.file_manager import FileManager
    from machineconfig.cluster.remote.models import RemoteMachineConfig
    from machineconfig.cluster.remote.job_params import JobParams


def transfer_sftp(ssh: SSH, config: RemoteMachineConfig, job_params: JobParams, file_manager: FileManager, data: list[str]) -> None:
    mkdir_cmd = f"import os; os.makedirs(os.path.dirname(os.path.expanduser(r'{file_manager.shell_script_path}')), exist_ok=True)"
    ssh.run_py_remotely(python_code=mkdir_cmd, uv_with=None, uv_project_dir=None, description="mkdir for shell script", verbose_output=False, strict_stderr=False, strict_return_code=False)
    if config.copy_repo:
        ssh.copy_from_here(source_path=job_params.repo_path_rh, target_rel2home=None, compress_with_zip=True, recursive=True, overwrite_existing=True)
    for a_path in data:
        is_dir = Path(a_path).expanduser().is_dir()
        ssh.copy_from_here(source_path=a_path, target_rel2home=None, compress_with_zip=is_dir, recursive=is_dir, overwrite_existing=True)
    ssh.copy_from_here(source_path=str(file_manager.job_root), target_rel2home=None, compress_with_zip=True, recursive=True, overwrite_existing=True)


def transfer_cloud(ssh: SSH, config: RemoteMachineConfig, job_params: JobParams, file_manager: FileManager, data: list[str]) -> None:
    cloud = config.cloud_name
    if cloud is None:
        raise ValueError("cloud_name must be set for cloud transfer")
    downloads: list[str] = []
    if config.copy_repo:
        downloads.append(f"rclone copy {cloud}:{_rel2home(job_params.repo_path_rh)} {job_params.repo_path_rh}")
    for a_path in data:
        downloads.append(f"rclone copy {cloud}:{_rel2home(a_path)} {a_path}")
    downloads.append(f"rclone copy {cloud}:{_rel2home(str(file_manager.job_root))} {file_manager.job_root}")
    download_cmd = "\n".join(downloads)
    shell_path = file_manager.shell_script_path.expanduser()
    existing = shell_path.read_text(encoding="utf-8") if shell_path.exists() else ""
    shell_path.write_text(download_cmd + "\n" + existing, encoding="utf-8")


def _rel2home(path_str: str) -> str:
    p = Path(path_str).expanduser()
    try:
        return str(p.relative_to(Path.home()))
    except ValueError:
        return str(p)
