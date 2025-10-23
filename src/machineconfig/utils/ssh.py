from typing import Callable, Optional, Any, Union, cast
import os
from pathlib import Path
import platform
from machineconfig.scripts.python.helpers_devops.cli_utils import MachineSpecs
import rich.console
from machineconfig.utils.terminal import Response
from machineconfig.utils.accessories import pprint, randstr
from machineconfig.utils.meta import lambda_to_python_script
UV_RUN_CMD = "$HOME/.local/bin/uv run" if platform.system() != "Windows" else """& "$env:USERPROFILE/.local/bin/uv" run"""
MACHINECONFIG_VERSION = "machineconfig>=6.81"
DEFAULT_PICKLE_SUBDIR = "tmp_results/tmp_scripts/ssh"

class SSH:
    @staticmethod
    def from_config_file(host: str) -> "SSH":
        """Create SSH instance from SSH config file entry."""
        return SSH(host=host, username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=False)
    def __init__(
        self, host: Optional[str], username: Optional[str], hostname: Optional[str], ssh_key_path: Optional[str], password: Optional[str], port: int, enable_compression: bool):
        self.password = password
        self.enable_compression = enable_compression

        self.host: Optional[str] = None
        self.hostname: str
        self.username: str
        self.port: int = port
        self.proxycommand: Optional[str] = None
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
        from machineconfig.scripts.python.helpers_devops.cli_utils import get_machine_specs
        self.local_specs: MachineSpecs = get_machine_specs()
        resp = self.run_shell(command=f"""~/.local/bin/utils get-machine-specs """, verbose_output=False, description="Getting remote machine specs", strict_stderr=False, strict_return_code=False)
        json_str = resp.op
        import ast
        self.remote_specs: MachineSpecs = cast(MachineSpecs, ast.literal_eval(json_str))
        self.terminal_responses: list[Response] = []
        
        from rich import inspect
        
        local_info = dict(distro=self.local_specs.get("distro"), system=self.local_specs.get("system"), home_dir=self.local_specs.get("home_dir"))
        remote_info = dict(distro=self.remote_specs.get("distro"), system=self.remote_specs.get("system"), home_dir=self.remote_specs.get("home_dir"))
        
        console = rich.console.Console()
        
        from io import StringIO
        local_buffer = StringIO()
        remote_buffer = StringIO()
        
        local_console = rich.console.Console(file=local_buffer, width=40)
        remote_console = rich.console.Console(file=remote_buffer, width=40)
        
        inspect(type("LocalInfo", (object,), local_info)(), value=False, title="SSHing From", docs=False, dunder=False, sort=False, console=local_console)
        inspect(type("RemoteInfo", (object,), remote_info)(), value=False, title="SSHing To", docs=False, dunder=False, sort=False, console=remote_console)
        
        local_lines = local_buffer.getvalue().split("\n")
        remote_lines = remote_buffer.getvalue().split("\n")
        
        max_lines = max(len(local_lines), len(remote_lines))
        for i in range(max_lines):
            left = local_lines[i] if i < len(local_lines) else ""
            right = remote_lines[i] if i < len(remote_lines) else ""
            console.print(f"{left:<42} {right}")

    def __enter__(self) -> "SSH":
        return self
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
    def close(self) -> None:
        if self.sftp is not None:
            self.sftp.close()
            self.sftp = None
        self.ssh.close()
    def restart_computer(self) -> Response:
        return self.run_shell(command="Restart-Computer -Force" if self.remote_specs["system"] == "Windows" else "sudo reboot", verbose_output=True, description="", strict_stderr=False, strict_return_code=False)
    def send_ssh_key(self) -> Response:
        self.copy_from_here(source_path="~/.ssh/id_rsa.pub", target_rel2home=None, compress_with_zip=False, recursive=False, overwrite_existing=False)
        if self.remote_specs["system"] != "Windows":
            raise RuntimeError("send_ssh_key is only supported for Windows remote machines")
        code_url = "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1"
        import urllib.request
        with urllib.request.urlopen(code_url) as response:
            code = response.read().decode("utf-8")
        return self.run_shell(command=code, verbose_output=True, description="", strict_stderr=False, strict_return_code=False)

    def get_remote_repr(self, add_machine: bool = False) -> str:
        return f"{self.username}@{self.hostname}:{self.port}" + (f" [{self.remote_specs['system']}][{self.remote_specs['distro']}]" if add_machine else "")
    def get_local_repr(self, add_machine: bool = False) -> str:
        import getpass
        return f"{getpass.getuser()}@{platform.node()}" + (f" [{platform.system()}][{self.local_specs['distro']}]" if add_machine else "")
    def get_ssh_conn_str(self, command: str) -> str:
        return "ssh " + (f" -i {self.ssh_key_path}" if self.ssh_key_path else "") + self.get_remote_repr(add_machine=False).replace(":", " -p ") + (f" -t {command} " if command != "" else " ")
    def __repr__(self) -> str:
        return f"local {self.get_local_repr(add_machine=True)} >>> SSH TO >>> remote {self.get_remote_repr(add_machine=True)}"

    def run_locally(self, command: str) -> Response:
        print(f"""💻 [LOCAL EXECUTION] Running command on node: {self.local_specs['system']} Command: {command}""")
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
        # self.terminal_responses.append(res)
        return res

    def _run_py_prep(self, python_code: str, uv_with: Optional[list[str]], uv_project_dir: Optional[str],) -> str:
        py_path = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/runpy_{randstr()}.py")
        py_path.parent.mkdir(parents=True, exist_ok=True)
        py_path.write_text(python_code, encoding="utf-8")
        self.copy_from_here(source_path=str(py_path), target_rel2home=None, compress_with_zip=False, recursive=False, overwrite_existing=False)
        if uv_with is not None and len(uv_with) > 0:
            with_clause = " --with " + '"' + ",".join(uv_with) + '"'
        else:
            with_clause = ""
        if uv_project_dir is not None:
            with_clause += f" --project {uv_project_dir}"
        else:
            with_clause += ""
        uv_cmd = f"""{UV_RUN_CMD} {with_clause} python {py_path.relative_to(Path.home())}"""
        return uv_cmd

    def run_py(self, python_code: str, uv_with: Optional[list[str]], uv_project_dir: Optional[str],
               description: str, verbose_output: bool, strict_stderr: bool, strict_return_code: bool) -> Response:
        uv_cmd = self._run_py_prep(python_code=python_code, uv_with=uv_with, uv_project_dir=uv_project_dir)
        return self.run_shell(command=uv_cmd, verbose_output=verbose_output, description=description or f"run_py on {self.get_remote_repr(add_machine=False)}", strict_stderr=strict_stderr, strict_return_code=strict_return_code)

    def run_lambda_function(self, func: Callable[..., Any], import_module: bool, uv_with: Optional[list[str]], uv_project_dir: Optional[str]):
        command = lambda_to_python_script(lmb=func, in_global=True, import_module=import_module)
        # turns ou that the code below for some reason runs but zellij doesn't start, looks like things are assigned to different user.
        # return self.run_py(python_code=command, uv_with=uv_with, uv_project_dir=uv_project_dir,
        #                    description=f"run_py_func {func.__name__} on {self.get_remote_repr(add_machine=False)}",
        #                    verbose_output=True, strict_stderr=True, strict_return_code=True)
        uv_cmd = self._run_py_prep(python_code=command, uv_with=uv_with, uv_project_dir=uv_project_dir)
        if self.remote_specs["system"] == "Linux":
            uv_cmd_modified = f'bash -l -c "{uv_cmd}"'
        else: uv_cmd_modified = uv_cmd
        # This works even withou the modified uv cmd:
        # from machineconfig.utils.code import run_shell_script
        # assert self.host is not None, "SSH host must be specified to run remote commands"
        # process = run_shell_script(f"ssh {self.host} -n '. ~/.profile; . ~/.bashrc; {uv_cmd}'")
        # return process
        return self.run_shell(command=uv_cmd_modified, verbose_output=True, description=f"run_py_func {func.__name__} on {self.get_remote_repr(add_machine=False)}", strict_stderr=True, strict_return_code=True)

    def _simple_sftp_get(self, remote_path: str, local_path: Path) -> None:
        """Simple SFTP get without any recursion or path expansion - for internal use only."""
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(remotepath=remote_path, localpath=str(local_path))

    def create_dir(self, path_rel2home: str, overwrite_existing: bool) -> None:
        """Helper to create a directory on remote machine and return its path."""
        def create_target_dir(target_rel2home: str, overwrite: bool):
            from pathlib import Path
            import shutil
            directory_path = Path(target_rel2home).expanduser()
            if overwrite and directory_path.exists():
                if directory_path.is_dir():
                    shutil.rmtree(directory_path)
                else:
                    directory_path.unlink()
            directory_path.parent.mkdir(parents=True, exist_ok=True)
        command = lambda_to_python_script(lmb=lambda: create_target_dir(target_rel2home=path_rel2home, overwrite=overwrite_existing), in_global=True, import_module=False)
        tmp_py_file = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/create_target_dir_{randstr()}.py")
        tmp_py_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_py_file.write_text(command, encoding="utf-8")
        # self.copy_from_here(source_path=str(tmp_py_file), target_rel2home=".tmp_file.py", compress_with_zip=False, recursive=False, overwrite_existing=True)
        assert self.sftp is not None
        tmp_remote_path = ".tmp_pyfile.py"
        self.sftp.put(localpath=str(tmp_py_file), remotepath=str(Path(self.remote_specs["home_dir"]).joinpath(tmp_remote_path)))
        self.run_shell(command=f"""{UV_RUN_CMD} python {tmp_remote_path}""", verbose_output=False, description=f"Creating target dir {path_rel2home}", strict_stderr=True, strict_return_code=True)

    def copy_from_here(self, source_path: str, target_rel2home: Optional[str], compress_with_zip: bool, recursive: bool, overwrite_existing: bool) -> None:
        if self.sftp is None: raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
        source_obj = Path(source_path).expanduser().absolute()
        if not source_obj.exists(): raise RuntimeError(f"SSH Error: source `{source_obj}` does not exist!")
        if target_rel2home is None:
            try: target_rel2home = str(source_obj.relative_to(Path.home()))
            except ValueError:
                raise RuntimeError(f"If target is not specified, source must be relative to home directory, but got: {source_obj}")
        if not compress_with_zip and source_obj.is_dir():
            if not recursive:
                raise RuntimeError(f"SSH Error: source `{source_obj}` is a directory! Set `recursive=True` for recursive sending or `compress_with_zip=True` to zip it first.")            
            file_paths_to_upload: list[Path] = [file_path for file_path in source_obj.rglob("*") if file_path.is_file()]
            self.create_dir(path_rel2home=target_rel2home, overwrite_existing=overwrite_existing)
            for idx, file_path in enumerate(file_paths_to_upload):
                print(f"   {idx + 1:03d}. {file_path}")
            for file_path in file_paths_to_upload:
                remote_file_target = Path(target_rel2home).joinpath(file_path.relative_to(source_obj))
                self.copy_from_here(source_path=str(file_path), target_rel2home=str(remote_file_target), compress_with_zip=False, recursive=False, overwrite_existing=overwrite_existing)
            return None
        if compress_with_zip:
            print("🗜️ ZIPPING ...")
            import shutil
            zip_path = Path(str(source_obj) + "_archive")
            if source_obj.is_dir():
                shutil.make_archive(str(zip_path), "zip", source_obj)
            else:
                shutil.make_archive(str(zip_path), "zip", source_obj.parent, source_obj.name)
            source_obj = Path(str(zip_path) + ".zip")
            if not target_rel2home.endswith(".zip"): target_rel2home = target_rel2home + ".zip"
        self.create_dir(path_rel2home=str(Path(target_rel2home).parent), overwrite_existing=overwrite_existing)
        print(f"""📤 [SFTP UPLOAD] Sending file: {repr(source_obj)}  ==>  Remote Path: {target_rel2home}""")
        try:
            with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
                if self.sftp is None:  # type: ignore[unreachable]
                    raise RuntimeError(f"SFTP connection lost for {self.hostname}")
                self.sftp.put(localpath=str(source_obj), remotepath=str(Path(self.remote_specs["home_dir"]).joinpath(target_rel2home)), callback=pbar.view_bar)
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
            command = lambda_to_python_script(lmb=lambda: unzip_archive(zip_file_path=str(Path(self.remote_specs["home_dir"]).joinpath(target_rel2home)), overwrite_flag=overwrite_existing), in_global=True, import_module=False)
            tmp_py_file = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/create_target_dir_{randstr()}.py")
            tmp_py_file.parent.mkdir(parents=True, exist_ok=True)
            tmp_py_file.write_text(command, encoding="utf-8")
            transferred_py_file = self.copy_from_here(source_path=str(tmp_py_file), target_rel2home=None, compress_with_zip=True, recursive=False, overwrite_existing=True)
            self.run_shell(command=f"""{UV_RUN_CMD} python {transferred_py_file}""", verbose_output=False, description=f"UNZIPPING {target_rel2home}", strict_stderr=True, strict_return_code=True)
            source_obj.unlink()
        return None

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
        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = lambda_to_python_script(lmb=lambda: check_is_dir(path_to_check=str(source_path), json_output_path=remote_json_output), in_global=True, import_module=False)
        response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description=f"Check if source `{source_path}` is a dir", verbose_output=False, strict_stderr=False, strict_return_code=False)
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Failed to check if {source_path} is directory - no response from remote")
        
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
        
        
        
        remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
        command = lambda_to_python_script(lmb=lambda: expand_source(path_to_expand=str(source_path), json_output_path=remote_json_output), in_global=True, import_module=False)
        response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description="Resolving source path by expanding user", verbose_output=False, strict_stderr=False, strict_return_code=False)
        remote_json_path = response.op.strip()
        if not remote_json_path:
            raise RuntimeError(f"Could not resolve source path {source_path} - no response from remote")
        
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
                
                
                
                remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
                command = lambda_to_python_script(lmb=lambda: search_files(directory_path=expanded_source, json_output_path=remote_json_output), in_global=True, import_module=False)
                response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description="Searching for files in source", verbose_output=False, strict_stderr=False, strict_return_code=False)
                remote_json_path = response.op.strip()
                if not remote_json_path:
                    raise RuntimeError(f"Could not resolve source path {source} - no response from remote")
                
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
                    
                    
                    
                    remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
                    command = lambda_to_python_script(lmb=lambda: collapse_to_home_dir(absolute_path=expanded_source, json_output_path=remote_json_output), in_global=True, import_module=False)
                    response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description="Finding default target via relative source path", verbose_output=False, strict_stderr=False, strict_return_code=False)
                    remote_json_path_dir = response.op.strip()
                    if not remote_json_path_dir:
                        raise RuntimeError("Could not resolve target path - no response from remote")
                    
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
            
            
            
            remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
            command = lambda_to_python_script(lmb=lambda: zip_source(path_to_zip=expanded_source, json_output_path=remote_json_output), in_global=True, import_module=False)
            response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description=f"Zipping source file {source}", verbose_output=False, strict_stderr=False, strict_return_code=False)
            remote_json_path = response.op.strip()
            if not remote_json_path:
                raise RuntimeError(f"Could not zip {source} - no response from remote")
            
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
            
            
            
            remote_json_output = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/return_{randstr()}.json").as_posix()
            command = lambda_to_python_script(lmb=lambda: collapse_to_home(absolute_path=expanded_source, json_output_path=remote_json_output), in_global=True, import_module=False)
            response = self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description="Finding default target via relative source path", verbose_output=False, strict_stderr=False, strict_return_code=False)
            remote_json_path = response.op.strip()
            if not remote_json_path:
                raise RuntimeError("Could not resolve target path - no response from remote")
            
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
            
            
            command = lambda_to_python_script(lmb=lambda: delete_temp_zip(path_to_delete=expanded_source), in_global=True, import_module=False)
            self.run_py(python_code=command, uv_with=[MACHINECONFIG_VERSION], uv_project_dir=None,  description="Cleaning temp zip files @ remote.", verbose_output=False, strict_stderr=True, strict_return_code=True)
        
        print("\n")
        return target_obj

if __name__ == "__main__":
    ssh = SSH(host="p51s", username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=False)
