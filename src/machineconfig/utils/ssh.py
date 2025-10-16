from typing import Callable, Optional, Any, Union
import os
from pathlib import Path
import rich.console
from machineconfig.utils.terminal import Response, MACHINE
from machineconfig.utils.accessories import pprint

UV_RUN_CMD = "$HOME/.local/bin/uv run"
MACHINECONFIG_VERSION = "machineconfig>=6.36"
DEFAULT_PICKLE_SUBDIR = "tmp_results/tmp_scripts/ssh"


class SSH:
    def __init__(
        self, host: Optional[str], username: Optional[str], hostname: Optional[str], ssh_key_path: Optional[str], password: Optional[str], port: int, enable_compression: bool):
        self.password = password
        self.enable_compression = enable_compression

        self.host: Optional[str] = None
        self.hostname: str
        self.username: str
        self.port: int = port
        self.proxycommand: Optional[str] = None
        import platform
        import paramiko  # type: ignore
        import getpass

        if isinstance(host, str):
            try:
                import paramiko.config as pconfig

                config = pconfig.SSHConfig.from_path(str(Path.home().joinpath(".ssh/config")))
                config_dict = config.lookup(host)
                self.hostname = config_dict["hostname"]
                self.username = config_dict["user"]
                self.host = host
                self.port = int(config_dict.get("port", port))
                identity_file_value = config_dict.get("identityfile", ssh_key_path)
                if isinstance(identity_file_value, list):
                    ssh_key_path = identity_file_value[0]
                else:
                    ssh_key_path = identity_file_value
                self.proxycommand = config_dict.get("proxycommand", None)
                if ssh_key_path is not None:
                    wildcard_identity_file = config.lookup("*").get("identityfile", ssh_key_path)
                    if isinstance(wildcard_identity_file, list):
                        ssh_key_path = wildcard_identity_file[0]
                    else:
                        ssh_key_path = wildcard_identity_file
            except (FileNotFoundError, KeyError):
                assert "@" in host or ":" in host, f"Host must be in the form of `username@hostname:port` or `username@hostname` or `hostname:port`, but it is: {host}"
                if "@" in host:
                    self.username, self.hostname = host.split("@")
                else:
                    self.username = username or getpass.getuser()
                    self.hostname = host
                if ":" in self.hostname:
                    self.hostname, port_ = self.hostname.split(":")
                    self.port = int(port_)
        elif username is not None and hostname is not None:
            self.username, self.hostname = username, hostname
            self.proxycommand = None
        else:
            print(f"Provided values: host={host}, username={username}, hostname={hostname}")
            raise ValueError("Either host or username and hostname must be provided.")

        self.ssh_key_path = str(Path(ssh_key_path).expanduser().absolute()) if ssh_key_path is not None else None
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pprint(dict(host=self.host, hostname=self.hostname, username=self.username, password="***", port=self.port, key_filename=self.ssh_key_path), title="SSHing To")
        sock = paramiko.ProxyCommand(self.proxycommand) if self.proxycommand is not None else None
        try:
            if password is None:
                allow_agent = True
                look_for_keys = True
            else:
                allow_agent = False
                look_for_keys = False
            self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password, port=self.port, key_filename=self.ssh_key_path, compress=self.enable_compression, sock=sock, allow_agent=allow_agent, look_for_keys=look_for_keys)  # type: ignore
        except Exception as _err:
            rich.console.Console().print_exception()
            self.password = getpass.getpass(f"Enter password for {self.username}@{self.hostname}: ")
            self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password, port=self.port, key_filename=self.ssh_key_path, compress=self.enable_compression, sock=sock, allow_agent=False, look_for_keys=False)  # type: ignore
        try:
            self.sftp: Optional[paramiko.SFTPClient] = self.ssh.open_sftp()
        except Exception as err:
            self.sftp = None
            print(f"""⚠️  WARNING: Failed to open SFTP connection to {self.hostname}. Error Details: {err}\nData transfer may be affected!""")
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, FileSizeColumn, TransferSpeedColumn

        class RichProgressWrapper:
            def __init__(self, **kwargs: Any):
                self.kwargs = kwargs
                self.progress: Optional[Progress] = None
                self.task: Optional[Any] = None

            def __enter__(self) -> "RichProgressWrapper":
                self.progress = Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), BarColumn(), FileSizeColumn(), TransferSpeedColumn())
                self.progress.start()
                self.task = self.progress.add_task("Transferring...", total=0)
                return self

            def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                if self.progress:
                    self.progress.stop()

            def view_bar(self, transferred: int, total: int) -> None:
                if self.progress and self.task is not None:
                    self.progress.update(self.task, completed=transferred, total=total)

        self.tqdm_wrap = RichProgressWrapper
        self._local_distro: Optional[str] = None
        self._remote_distro: Optional[str] = None
        self._remote_machine: Optional[MACHINE] = None
        self.terminal_responses: list[Response] = []
        self.platform = platform

    def __enter__(self) -> "SSH":
        return self
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
    def close(self) -> None:
        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None
        self.ssh.close()
    def get_remote_machine(self) -> MACHINE:
        if self._remote_machine is None:
            windows_test1 = self.run_shell(command="$env:OS", verbose_output=False, description="Testing Remote OS Type", strict_stderr=False, strict_return_code=False).op
            windows_test2 = self.run_shell(command="echo %OS%", verbose_output=False, description="Testing Remote OS Type Again", strict_stderr=False, strict_return_code=False).op
            if windows_test1 == "Windows_NT" or windows_test2 == "Windows_NT":
                self._remote_machine = "Windows"
            else:
                self._remote_machine = "Linux"
        return self._remote_machine
    def get_local_distro(self) -> str:
        if self._local_distro is None:
            command = f"""{UV_RUN_CMD} --with distro python -c "import distro; print(distro.name(pretty=True))" """
            import subprocess
            res = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
            self._local_distro = res
            return res
        return self._local_distro
    def get_remote_distro(self) -> str:
        if self._remote_distro is None:
            command_str = f"""{UV_RUN_CMD} --with distro python -c "import distro; print(distro.name(pretty=True))" """
            res = self.run_shell(command=command_str, verbose_output=True, description="", strict_stderr=False, strict_return_code=False)
            self._remote_distro = res.op_if_successfull_or_default() or ""
        return self._remote_distro
    def restart_computer(self) -> Response:
        return self.run_shell(command="Restart-Computer -Force" if self.get_remote_machine() == "Windows" else "sudo reboot", verbose_output=True, description="", strict_stderr=False, strict_return_code=False)
    def send_ssh_key(self) -> Response:
        self.copy_from_here(source_path=Path("~/.ssh/id_rsa.pub"), target_path=None, compress_with_zip=False, recursive=False, overwrite_existing=False)
        if self.get_remote_machine() != "Windows":
            raise RuntimeError("send_ssh_key is only supported for Windows remote machines")
        code_url = "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1"
        import urllib.request
        with urllib.request.urlopen(code_url) as response:
            code = response.read().decode("utf-8")
        return self.run_shell(command=code, verbose_output=True, description="", strict_stderr=False, strict_return_code=False)

    def get_remote_repr(self, add_machine: bool = False) -> str:
        return f"{self.username}@{self.hostname}:{self.port}" + (f" [{self.get_remote_machine()}][{self.get_remote_distro()}]" if add_machine else "")
    def get_local_repr(self, add_machine: bool = False) -> str:
        import getpass
        return f"{getpass.getuser()}@{self.platform.node()}" + (f" [{self.platform.system()}][{self.get_local_distro()}]" if add_machine else "")
    def get_ssh_conn_str(self, command: str) -> str:
        return "ssh " + (f" -i {self.ssh_key_path}" if self.ssh_key_path else "") + self.get_remote_repr(add_machine=False).replace(":", " -p ") + (f" -t {command} " if command != "" else " ")
    def __repr__(self) -> str:
        return f"local {self.get_local_repr(add_machine=True)} >>> SSH TO >>> remote {self.get_remote_repr(add_machine=True)}"

    def run_locally(self, command: str) -> Response:
        print(f"""💻 [LOCAL EXECUTION] Running command on node: {self.platform.node()} Command: {command}""")
        res = Response(cmd=command)
        res.output.returncode = os.system(command)
        return res


    def run_shell(self, command: str, verbose_output: bool, description: str, strict_stderr: bool, strict_return_code: bool) -> Response:
        raw = self.ssh.exec_command(command)
        res = Response(stdin=raw[0], stdout=raw[1], stderr=raw[2], cmd=command, desc=description)  # type: ignore
        if verbose_output:
            res.print()
        else:
            res.capture().print_if_unsuccessful(desc=description, strict_err=strict_stderr, strict_returncode=strict_return_code, assert_success=False)
        self.terminal_responses.append(res)
        return res
    def run_py(self, python_code: str, dependencies: list[str], venv_path: Optional[str],
               description: str, verbose_output: bool, strict_stderr: bool, strict_return_code: bool) -> Response:
        from machineconfig.utils.accessories import randstr
        cmd_path = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/runpy_{randstr()}.py")
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        cmd_path.write_text(python_code, encoding="utf-8")
        self.copy_from_here(source_path=cmd_path, target_path=None, compress_with_zip=False, recursive=False, overwrite_existing=False)
        if len(dependencies) > 0:
            with_clause = " --with " + '"', ",".join(dependencies) + '"'
        else:
            with_clause = ""
        uv_cmd = f"""{UV_RUN_CMD} {with_clause} python {cmd_path.relative_to(Path.home())}"""
        if venv_path is not None:
            if self.get_remote_machine() == "Windows":
                venv_export = f"$env:VIRTUAL_ENV='{venv_path}';"
                uv_cmd = venv_export + uv_cmd
            else:
                venv_export = f"VIRTUAL_ENV={venv_path}"
                uv_cmd = venv_export + " " + uv_cmd
        return self.run_shell(command=uv_cmd, verbose_output=verbose_output, description=description or f"run_py on {self.get_remote_repr(add_machine=False)}", strict_stderr=strict_stderr, strict_return_code=strict_return_code)

    def run_py_func(self, func: Callable[..., Any], dependencies: list[str], venv_path: Optional[str]) -> Response:
        from machineconfig.utils.meta import function_to_script
        command = function_to_script(func=func, call_with_kwargs={})
        return self.run_py(python_code=command, dependencies=dependencies, venv_path=venv_path, description=f"run_py_func {func.__name__} on {self.get_remote_repr(add_machine=False)}", verbose_output=True, strict_stderr=True, strict_return_code=True)

    def _simple_sftp_get(self, remote_path: str, local_path: Path) -> None:
        """Simple SFTP get without any recursion or path expansion - for internal use only."""
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(remotepath=remote_path, localpath=str(local_path))

    def _create_remote_target_dir(self, target_path: Union[str, Path], overwrite_existing: bool) -> str:
        """Helper to create a directory on remote machine and return its path."""
        def create_target_dir(target_dir_path: str, overwrite: bool, json_output_path: str) -> str:
            from pathlib import Path
            import shutil
            import json
            directory_path = Path(target_dir_path).expanduser()
            if overwrite and directory_path.exists():
                if directory_path.is_dir():
                    shutil.rmtree(directory_path)
                else:
                    directory_path.unlink()
            directory_path.parent.mkdir(parents=True, exist_ok=True)
            result_path_posix = directory_path.as_posix()
            json_result_path = Path(json_output_path)
            json_result_path.parent.mkdir(parents=True, exist_ok=True)
            json_result_path.write_text(json.dumps(result_path_posix, indent=2), encoding="utf-8")
            print(json_result_path.as_posix())
            return result_path_posix
        from machineconfig.utils.meta import function_to_script
        from machineconfig.utils.accessories import randstr
        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = function_to_script(func=create_target_dir, call_with_kwargs={"target_dir_path": Path(target_path).as_posix(), "overwrite": overwrite_existing, "json_output_path": remote_json_output})
        response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description=f"Creating target directory `{Path(target_path).parent.as_posix()}` @ {self.get_remote_repr(add_machine=False)}", verbose_output=False, strict_stderr=False, strict_return_code=False)
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Failed to create target directory {target_path} - no response from remote")
        from machineconfig.utils.accessories import randstr
        local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
        self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
        import json
        try:
            result = json.loads(local_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError) as err:
            raise RuntimeError(f"Failed to create target directory {target_path} - invalid JSON response: {err}") from err
        finally:
            if local_json.exists():
                local_json.unlink()
        assert isinstance(result, str), f"Failed to create target directory {target_path} on remote"
        return result


    def copy_from_here(self, source_path: Union[str, Path], target_path: Optional[Union[str, Path]], compress_with_zip: bool, recursive: bool, overwrite_existing: bool) -> Path:
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
        
        source_obj = Path(source_path).expanduser().absolute()
        if not source_obj.exists():
            raise RuntimeError(f"SSH Error: source `{source_obj}` does not exist!")
        
        if target_path is None:
            try:
                target_path_relative = source_obj.relative_to(Path.home())
                target_path = Path("~") / target_path_relative
            except ValueError:
                raise RuntimeError(f"If target is not specified, source must be relative to home directory, but got: {source_obj}")
        
        if not compress_with_zip and source_obj.is_dir():
            if not recursive:
                raise RuntimeError(f"SSH Error: source `{source_obj}` is a directory! Set `recursive=True` for recursive sending or `compress_with_zip=True` to zip it first.")            
            file_paths_to_upload: list[Path] = [file_path for file_path in source_obj.rglob("*") if file_path.is_file()]
            remote_root = self._create_remote_target_dir(target_path=target_path, overwrite_existing=overwrite_existing)
            for idx, file_path in enumerate(file_paths_to_upload):
                print(f"   {idx + 1:03d}. {file_path}")
            for file_path in file_paths_to_upload:
                remote_file_target = Path(remote_root).joinpath(file_path.relative_to(source_obj))
                self.copy_from_here(source_path=file_path, target_path=remote_file_target, compress_with_zip=False, recursive=False, overwrite_existing=overwrite_existing)
            return Path(remote_root)
        if compress_with_zip:
            print("🗜️ ZIPPING ...")
            import shutil
            zip_path = Path(str(source_obj) + "_archive")
            if source_obj.is_dir():
                shutil.make_archive(str(zip_path), "zip", source_obj)
            else:
                shutil.make_archive(str(zip_path), "zip", source_obj.parent, source_obj.name)
            source_obj = Path(str(zip_path) + ".zip")
            if not str(target_path).endswith(".zip"):
                target_path = Path(str(target_path) + ".zip")
        remotepath_str = self._create_remote_target_dir(target_path=target_path, overwrite_existing=overwrite_existing)
        remotepath = Path(remotepath_str)        
        print(f"""📤 [SFTP UPLOAD] Sending file: {repr(source_obj)}  ==>  Remote Path: {remotepath.as_posix()}""")
        try:
            with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
                if self.sftp is None:  # type: ignore[unreachable]
                    raise RuntimeError(f"SFTP connection lost for {self.hostname}")
                self.sftp.put(localpath=str(source_obj), remotepath=remotepath.as_posix(), callback=pbar.view_bar)  # type: ignore
        except Exception:
            if compress_with_zip and source_obj.exists() and str(source_obj).endswith("_archive.zip"):
                source_obj.unlink()
            raise
        
        if compress_with_zip:
            def unzip_archive(zip_file_path: str, overwrite_flag: bool) -> None:
                from pathlib import Path
                import shutil
                import zipfile
                archive_path = Path(zip_file_path).expanduser()
                extraction_directory = archive_path.parent / archive_path.stem
                if overwrite_flag and extraction_directory.exists():
                    shutil.rmtree(extraction_directory)
                with zipfile.ZipFile(archive_path, "r") as archive_handle:
                    archive_handle.extractall(extraction_directory)
                archive_path.unlink()
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=unzip_archive, call_with_kwargs={"zip_file_path": remotepath.as_posix(), "overwrite_flag": overwrite_existing})
            _resp = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description=f"UNZIPPING {remotepath.as_posix()}", verbose_output=False, strict_stderr=True, strict_return_code=True)
            source_obj.unlink()
            print("\n")        
        return source_obj

    def _check_remote_is_dir(self, source_path: Union[str, Path]) -> bool:
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
        
        from machineconfig.utils.meta import function_to_script
        from machineconfig.utils.accessories import randstr
        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = function_to_script(func=check_is_dir, call_with_kwargs={"path_to_check": str(source_path), "json_output_path": remote_json_output})
        response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description=f"Check if source `{source_path}` is a dir", verbose_output=False, strict_stderr=False, strict_return_code=False)
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Failed to check if {source_path} is directory - no response from remote")
        from machineconfig.utils.accessories import randstr
        local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
        self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
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

    def _expand_remote_path(self, source_path: Union[str, Path]) -> str:
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
        
        from machineconfig.utils.meta import function_to_script
        from machineconfig.utils.accessories import randstr
        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = function_to_script(func=expand_source, call_with_kwargs={"path_to_expand": str(source_path), "json_output_path": remote_json_output})
        response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description="Resolving source path by expanding user", verbose_output=False, strict_stderr=False, strict_return_code=False)
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Could not resolve source path {source_path} - no response from remote")
        from machineconfig.utils.accessories import randstr
        local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
        self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
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

    def copy_to_here(self, source: Union[str, Path], target: Optional[Union[str, Path]], compress_with_zip: bool = False, recursive: bool = False, internal_call: bool = False) -> Path:
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
        
        if not internal_call:
            print(f"{'⬇️' * 5} SFTP DOWNLOADING FROM `{source}` TO `{target}`")
        
        source_obj = Path(source)
        expanded_source = self._expand_remote_path(source_path=source_obj)
        
        if not compress_with_zip:
            is_dir = self._check_remote_is_dir(source_path=expanded_source)
            
            if is_dir:
                if not recursive:
                    raise RuntimeError(f"SSH Error: source `{source_obj}` is a directory! Set recursive=True for recursive transfer or compress_with_zip=True to zip it.")
                
                def search_files(directory_path: str, json_output_path: str) -> list[str]:
                    from pathlib import Path
                    import json
                    file_paths_list = [file_path.as_posix() for file_path in Path(directory_path).expanduser().absolute().rglob("*") if file_path.is_file()]
                    json_result_path = Path(json_output_path)
                    json_result_path.parent.mkdir(parents=True, exist_ok=True)
                    json_result_path.write_text(json.dumps(file_paths_list, indent=2), encoding="utf-8")
                    print(json_result_path.as_posix())
                    return file_paths_list
                
                from machineconfig.utils.meta import function_to_script
                from machineconfig.utils.accessories import randstr
                remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
                command = function_to_script(func=search_files, call_with_kwargs={"directory_path": expanded_source, "json_output_path": remote_json_output})
                response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description="Searching for files in source", verbose_output=False, strict_stderr=False, strict_return_code=False)
                remote_json_path = response.op.strip()
                if not remote_json_path:
                    raise RuntimeError(f"Could not resolve source path {source} - no response from remote")
                from machineconfig.utils.accessories import randstr
                local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
                self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
                import json
                try:
                    source_list_str = json.loads(local_json.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, FileNotFoundError) as err:
                    raise RuntimeError(f"Could not resolve source path {source} - invalid JSON response: {err}") from err
                finally:
                    if local_json.exists():
                        local_json.unlink()
                assert isinstance(source_list_str, list), f"Could not resolve source path {source}"
                file_paths_to_download = [Path(file_path_str) for file_path_str in source_list_str]
                
                if target is None:
                    def collapse_to_home_dir(absolute_path: str, json_output_path: str) -> str:
                        from pathlib import Path
                        import json
                        source_absolute_path = Path(absolute_path).expanduser().absolute()
                        try:
                            relative_to_home = source_absolute_path.relative_to(Path.home())
                            collapsed_path_posix = (Path("~") / relative_to_home).as_posix()
                            json_result_path = Path(json_output_path)
                            json_result_path.parent.mkdir(parents=True, exist_ok=True)
                            json_result_path.write_text(json.dumps(collapsed_path_posix, indent=2), encoding="utf-8")
                            print(json_result_path.as_posix())
                            return collapsed_path_posix
                        except ValueError:
                            raise RuntimeError(f"Source path must be relative to home directory: {source_absolute_path}")
                    
                    from machineconfig.utils.meta import function_to_script
                    from machineconfig.utils.accessories import randstr
                    remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
                    command = function_to_script(func=collapse_to_home_dir, call_with_kwargs={"absolute_path": expanded_source, "json_output_path": remote_json_output})
                    response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description="Finding default target via relative source path", verbose_output=False, strict_stderr=False, strict_return_code=False)
                    remote_json_path_dir = response.op.strip()
                    if not remote_json_path_dir:
                        raise RuntimeError("Could not resolve target path - no response from remote")
                    from machineconfig.utils.accessories import randstr
                    local_json_dir = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
                    self._simple_sftp_get(remote_path=remote_json_path_dir, local_path=local_json_dir)
                    import json
                    try:
                        target_dir_str = json.loads(local_json_dir.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, FileNotFoundError) as err:
                        raise RuntimeError(f"Could not resolve target path - invalid JSON response: {err}") from err
                    finally:
                        if local_json_dir.exists():
                            local_json_dir.unlink()
                    assert isinstance(target_dir_str, str), "Could not resolve target path"
                    target = Path(target_dir_str)
                
                target_dir = Path(target).expanduser().absolute()
                
                for idx, file_path in enumerate(file_paths_to_download):
                    print(f"   {idx + 1:03d}. {file_path}")
                
                for file_path in file_paths_to_download:
                    local_file_target = target_dir.joinpath(Path(file_path).relative_to(expanded_source))
                    self.copy_to_here(source=file_path, target=local_file_target, compress_with_zip=False, recursive=False, internal_call=True)
                
                return target_dir
        
        if compress_with_zip:
            print("🗜️ ZIPPING ...")
            def zip_source(path_to_zip: str, json_output_path: str) -> str:
                from pathlib import Path
                import shutil
                import json
                source_to_compress = Path(path_to_zip).expanduser().absolute()
                archive_base_path = source_to_compress.parent / (source_to_compress.name + "_archive")
                if source_to_compress.is_dir():
                    shutil.make_archive(str(archive_base_path), "zip", source_to_compress)
                else:
                    shutil.make_archive(str(archive_base_path), "zip", source_to_compress.parent, source_to_compress.name)
                zip_file_path = str(archive_base_path) + ".zip"
                json_result_path = Path(json_output_path)
                json_result_path.parent.mkdir(parents=True, exist_ok=True)
                json_result_path.write_text(json.dumps(zip_file_path, indent=2), encoding="utf-8")
                print(json_result_path.as_posix())
                return zip_file_path
            
            from machineconfig.utils.meta import function_to_script
            from machineconfig.utils.accessories import randstr
            remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
            command = function_to_script(func=zip_source, call_with_kwargs={"path_to_zip": expanded_source, "json_output_path": remote_json_output})
            response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description=f"Zipping source file {source}", verbose_output=False, strict_stderr=False, strict_return_code=False)
            remote_json_path = response.op.strip()
            if not remote_json_path:
                raise RuntimeError(f"Could not zip {source} - no response from remote")
            from machineconfig.utils.accessories import randstr
            local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
            self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
            import json
            try:
                zipped_path = json.loads(local_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError) as err:
                raise RuntimeError(f"Could not zip {source} - invalid JSON response: {err}") from err
            finally:
                if local_json.exists():
                    local_json.unlink()
            assert isinstance(zipped_path, str), f"Could not zip {source}"
            source_obj = Path(zipped_path)
            expanded_source = zipped_path
        
        if target is None:
            def collapse_to_home(absolute_path: str, json_output_path: str) -> str:
                from pathlib import Path
                import json
                source_absolute_path = Path(absolute_path).expanduser().absolute()
                try:
                    relative_to_home = source_absolute_path.relative_to(Path.home())
                    collapsed_path_posix = (Path("~") / relative_to_home).as_posix()
                    json_result_path = Path(json_output_path)
                    json_result_path.parent.mkdir(parents=True, exist_ok=True)
                    json_result_path.write_text(json.dumps(collapsed_path_posix, indent=2), encoding="utf-8")
                    print(json_result_path.as_posix())
                    return collapsed_path_posix
                except ValueError:
                    raise RuntimeError(f"Source path must be relative to home directory: {source_absolute_path}")
            
            from machineconfig.utils.meta import function_to_script
            from machineconfig.utils.accessories import randstr
            remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
            command = function_to_script(func=collapse_to_home, call_with_kwargs={"absolute_path": expanded_source, "json_output_path": remote_json_output})
            response = self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description="Finding default target via relative source path", verbose_output=False, strict_stderr=False, strict_return_code=False)
            remote_json_path = response.op.strip()
            if not remote_json_path:
                raise RuntimeError("Could not resolve target path - no response from remote")
            from machineconfig.utils.accessories import randstr
            local_json = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/local_{randstr()}.json")
            self._simple_sftp_get(remote_path=remote_json_path, local_path=local_json)
            import json
            try:
                target_str = json.loads(local_json.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError) as err:
                raise RuntimeError(f"Could not resolve target path - invalid JSON response: {err}") from err
            finally:
                if local_json.exists():
                    local_json.unlink()
            assert isinstance(target_str, str), "Could not resolve target path"
            target = Path(target_str)
            assert str(target).startswith("~"), f"If target is not specified, source must be relative to home.\n{target=}"
        
        target_obj = Path(target).expanduser().absolute()
        target_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if compress_with_zip and target_obj.suffix != ".zip":
            target_obj = target_obj.with_suffix(target_obj.suffix + ".zip")
        
        print(f"""📥 [DOWNLOAD] Receiving: {expanded_source}  ==>  Local Path: {target_obj}""")
        try:
            with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
                if self.sftp is None:  # type: ignore[unreachable]
                    raise RuntimeError(f"SFTP connection lost for {self.hostname}")
                self.sftp.get(remotepath=expanded_source, localpath=str(target_obj), callback=pbar.view_bar)  # type: ignore
        except Exception:
            if target_obj.exists():
                target_obj.unlink()
            raise
        
        if compress_with_zip:
            import zipfile
            extract_to = target_obj.parent / target_obj.stem
            with zipfile.ZipFile(target_obj, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            target_obj.unlink()
            target_obj = extract_to
            
            def delete_temp_zip(path_to_delete: str) -> None:
                from pathlib import Path
                import shutil
                file_or_dir_path = Path(path_to_delete)
                if file_or_dir_path.exists():
                    if file_or_dir_path.is_dir():
                        shutil.rmtree(file_or_dir_path)
                    else:
                        file_or_dir_path.unlink()
            
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=delete_temp_zip, call_with_kwargs={"path_to_delete": expanded_source})
            self.run_py(python_code=command, dependencies=[MACHINECONFIG_VERSION], venv_path=None, description="Cleaning temp zip files @ remote.", verbose_output=False, strict_stderr=True, strict_return_code=True)
        
        print("\n")
        return target_obj

