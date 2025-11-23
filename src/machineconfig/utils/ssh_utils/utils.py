
from pathlib import Path
from machineconfig.utils.accessories import randstr
from machineconfig.utils.meta import lambda_to_python_script
from machineconfig.utils.ssh_utils.abc import MACHINECONFIG_VERSION, DEFAULT_PICKLE_SUBDIR
from machineconfig.utils.code import get_uv_command
from typing import Union


def create_dir_and_check_if_exists(self: "SSH", path_rel2home: str, overwrite_existing: bool) -> None:
    """Helper to create a directory on remote machine and return its path."""

    def create_target_dir(target_rel2home: str, overwrite: bool):
        from pathlib import Path
        import shutil
        target_path_abs = Path(target_rel2home).expanduser()
        if not target_path_abs.is_absolute():
            target_path_abs = Path.home().joinpath(target_path_abs)
        if overwrite and target_path_abs.exists():
            if str(target_path_abs) == str(Path.home()):
                raise RuntimeError("Refusing to overwrite home directory!")
            if target_path_abs.is_dir():
                shutil.rmtree(target_path_abs)
            else:
                target_path_abs.unlink()
        print(f"Creating directory for path: {target_path_abs}")
        target_path_abs.parent.mkdir(parents=True, exist_ok=True)
    command = lambda_to_python_script(
        lambda: create_target_dir(target_rel2home=path_rel2home, overwrite=overwrite_existing),
        in_global=True, import_module=False
    )
    tmp_py_file = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/create_target_dir_{randstr()}.py")
    tmp_py_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_py_file.write_text(command, encoding="utf-8")
    assert self.sftp is not None
    tmp_remote_path = ".tmp_pyfile.py"
    self.sftp.put(localpath=str(tmp_py_file), remotepath=str(Path(self.remote_specs["home_dir"]).joinpath(tmp_remote_path)))
    resp = self.run_shell_cmd_on_remote(
        command=f"""{get_uv_command(platform=self.remote_specs['system'])} run python {tmp_remote_path}""",
        verbose_output=False,
        description=f"Creating target dir {path_rel2home}",
        strict_stderr=True,
        strict_return_code=True,
    )
    resp.print(desc=f"Created target dir {path_rel2home}")


def check_remote_is_dir(self: "SSH", source_path: Union[str, Path]) -> bool:
    """Helper to check if a remote path is a directory."""

    def check_is_dir(path_to_check: str, json_output_path: str) -> bool:
        from pathlib import Path
        import json

        is_directory = Path(path_to_check).expanduser().absolute().is_dir()
        json_result_path = Path(json_output_path)
        json_result_path.parent.mkdir(parents=True, exist_ok=True)
        json_result_path.write_text(json.dumps(is_directory, indent=2), encoding="utf-8")
        print(json_result_path.as_posix())
        return is_directory

    remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
    command = lambda_to_python_script(
        lambda: check_is_dir(path_to_check=str(source_path), json_output_path=remote_json_output),
        in_global=True, import_module=False
    )
    response = self.run_py_remotely(
        python_code=command,
        uv_with=[MACHINECONFIG_VERSION],
        uv_project_dir=None,
        description=f"Check if source `{source_path}` is a dir",
        verbose_output=False,
        strict_stderr=False,
        strict_return_code=False,
    )
    remote_json_path = response.op.strip()
    if not remote_json_path:
        raise RuntimeError(f"Failed to check if {source_path} is directory - no response from remote")

    local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
    self.simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
    import json

    try:
        result = json.loads(local_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as err:
        raise RuntimeError(f"Failed to check if {source_path} is directory - invalid JSON response: {err}") from err
    finally:
        if local_json.exists():
            local_json.unlink()
    assert isinstance(result, bool), f"Failed to check if {source_path} is directory"
    return result

def expand_remote_path(self: "SSH", source_path: Union[str, Path]) -> str:
    """Helper to expand a path on the remote machine."""

    def expand_source(path_to_expand: str, json_output_path: str) -> str:
        from pathlib import Path
        import json

        expanded_path_posix = Path(path_to_expand).expanduser().absolute().as_posix()
        json_result_path = Path(json_output_path)
        json_result_path.parent.mkdir(parents=True, exist_ok=True)
        json_result_path.write_text(json.dumps(expanded_path_posix, indent=2), encoding="utf-8")
        print(json_result_path.as_posix())
        return expanded_path_posix

    remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
    command = lambda_to_python_script(
        lambda: expand_source(path_to_expand=str(source_path), json_output_path=remote_json_output),
        in_global=True, import_module=False
    )
    response = self.run_py_remotely(
        python_code=command,
        uv_with=[MACHINECONFIG_VERSION],
        uv_project_dir=None,
        description="Resolving source path by expanding user",
        verbose_output=False,
        strict_stderr=False,
        strict_return_code=False,
    )
    remote_json_path = response.op.strip()
    if not remote_json_path:
        raise RuntimeError(f"Could not resolve source path {source_path} - no response from remote")

    local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
    self.simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
    import json

    try:
        result = json.loads(local_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as err:
        raise RuntimeError(f"Could not resolve source path {source_path} - invalid JSON response: {err}") from err
    finally:
        if local_json.exists():
            local_json.unlink()
    assert isinstance(result, str), f"Could not resolve source path {source_path}"
    return result


if __name__ == "__main__":
    from machineconfig.utils.ssh import SSH
