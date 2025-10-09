from typing import Optional, Any, Union
import os
from pathlib import Path
import rich.console
from machineconfig.utils.terminal import Response, MACHINE
from machineconfig.utils.accessories import pprint

UV_RUN_CMD = "$HOME/.local/bin/uv run"
MACHINECONFIG_VERSION = "machineconfig>=5.67"
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
                tmp = config_dict.get("identityfile", sshkey)
                if isinstance(tmp, list):
                    sshkey = tmp[0]
                else:
                    sshkey = tmp
                self.proxycommand = config_dict.get("proxycommand", None)
                if sshkey is not None:
                    tmp = config.lookup("*").get("identityfile", sshkey)
                    if isinstance(tmp, list):
                        sshkey = tmp[0]
                    else:
                        sshkey = tmp
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

        self.sshkey = str(Path(sshkey).expanduser().absolute()) if sshkey is not None else None  # no need to pass sshkey if it was configured properly already
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pprint(dict(host=self.host, hostname=self.hostname, username=self.username, password="***", port=self.port, key_filename=self.sshkey), title="SSHing To")
        sock = paramiko.ProxyCommand(self.proxycommand) if self.proxycommand is not None else None
        try:
            if pwd is None:
                allow_agent = True
                look_for_keys = True
            else:
                allow_agent = False
                look_for_keys = False
            self.ssh.connect(hostname=self.hostname, username=self.username, password=self.pwd, port=self.port, key_filename=self.sshkey, compress=self.compress, sock=sock, allow_agent=allow_agent, look_for_keys=look_for_keys)  # type: ignore
        except Exception as _err:
            rich.console.Console().print_exception()
            self.pwd = getpass.getpass(f"Enter password for {self.username}@{self.hostname}: ")
            self.ssh.connect(hostname=self.hostname, username=self.username, password=self.pwd, port=self.port, key_filename=self.sshkey, compress=self.compress, sock=sock, allow_agent=False, look_for_keys=False)  # type: ignore
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
            windows_test1 = self.run("$env:OS", verbose=False, desc="Testing Remote OS Type").op
            windows_test2 = self.run("echo %OS%", verbose=False, desc="Testing Remote OS Type Again").op
            if windows_test1 == "Windows_NT" or windows_test2 == "Windows_NT":
                self._remote_machine = "Windows"
            else:
                self._remote_machine = "Linux"
        return self._remote_machine

    def get_local_distro(self) -> str:
        if self._local_distro is None:
            command = """uv run --with distro python -c "import distro; print(distro.name(pretty=True))" """
            import subprocess
            res = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
            self._local_distro = res
            return res
        return self._local_distro

    def get_remote_distro(self) -> str:
        if self._remote_distro is None:
            cmd = f"""{UV_RUN_CMD} --with distro python -c "import distro; print(distro.name(pretty=True))" """
            res = self.run(cmd)
            self._remote_distro = res.op_if_successfull_or_default() or ""
        return self._remote_distro

    def restart_computer(self) -> Response:
        return self.run("Restart-Computer -Force" if self.get_remote_machine() == "Windows" else "sudo reboot")

    def send_ssh_key(self) -> Response:
        self.copy_from_here(source=Path("~/.ssh/id_rsa.pub"), target=None)
        if self.get_remote_machine() != "Windows":
            raise RuntimeError("send_ssh_key is only supported for Windows remote machines")
        code_url = "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1"
        import urllib.request
        with urllib.request.urlopen(code_url) as response:
            code = response.read().decode("utf-8")
        return self.run(cmd=code)

    def copy_env_var(self, name: str) -> Response:
        if self.get_remote_machine() != "Linux":
            raise RuntimeError("copy_env_var is only supported for Linux remote machines")
        env_value = os.environ.get(name)
        if env_value is None:
            raise RuntimeError(f"Environment variable {name} not found in local environment")
        return self.run(cmd=f"{name}={env_value}; export {name}")

    def get_remote_repr(self, add_machine: bool = False) -> str:
        return f"{self.username}@{self.hostname}:{self.port}" + (f" [{self.get_remote_machine()}][{self.get_remote_distro()}]" if add_machine else "")

    def get_local_repr(self, add_machine: bool = False) -> str:
        import getpass

        return f"{getpass.getuser()}@{self.platform.node()}" + (f" [{self.platform.system()}][{self.get_local_distro()}]" if add_machine else "")

    def __repr__(self) -> str:
        return f"local {self.get_local_repr(add_machine=True)} >>> SSH TO >>> remote {self.get_remote_repr(add_machine=True)}"

    def run_locally(self, command: str) -> Response:
        print(f"""💻 [LOCAL EXECUTION] Running command on node: {self.platform.node()} Command: {command}""")
        res = Response(cmd=command)
        res.output.returncode = os.system(command)
        return res

    def get_ssh_conn_str(self, cmd: str = "") -> str:
        return "ssh " + (f" -i {self.sshkey}" if self.sshkey else "") + self.get_remote_repr().replace(":", " -p ") + (f" -t {cmd} " if cmd != "" else " ")

    def run(self, cmd: str, verbose: bool = True, desc: str = "", strict_err: bool = False, strict_returncode: bool = False) -> Response:
        raw = self.ssh.exec_command(cmd)
        res = Response(stdin=raw[0], stdout=raw[1], stderr=raw[2], cmd=cmd, desc=desc)  # type: ignore
        if verbose:
            res.print()
        else:
            res.capture().print_if_unsuccessful(desc=desc, strict_err=strict_err, strict_returncode=strict_returncode, assert_success=False)
        self.terminal_responses.append(res)
        return res
    def _create_remote_target_dir(self, target_path: Union[str, Path], overwrite: bool) -> str:
        """Helper to create a directory on remote machine and return its path."""
        def create_target_dir(item: str, overwrite: bool) -> str:
            from pathlib import Path
            import shutil
            path = Path(item).expanduser()
            if overwrite and path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            path.parent.mkdir(parents=True, exist_ok=True)
            obj = path.as_posix()
            return obj
        
        from machineconfig.utils.meta import function_to_script
        command = function_to_script(func=create_target_dir, call_with_kwargs={"item": Path(target_path).as_posix(), "overwrite": overwrite})
        result = self.run_py(command, desc=f"Creating target directory `{Path(target_path).parent.as_posix()}` @ {self.get_remote_repr()}", return_obj=True, verbose=False)
        assert isinstance(result, str), f"Failed to create target directory {target_path} on remote"
        return result

    def run_py(self, cmd: str, desc: str = "", return_obj: bool = False, verbose: bool = True, strict_err: bool = False, strict_returncode: bool = False) -> Union[Any, Response]:
        from machineconfig.utils.accessories import randstr
        cmd_path = Path.home().joinpath(f"{DEFAULT_PICKLE_SUBDIR}/runpy_{randstr()}.py")
        cmd_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not return_obj:
            cmd_path.write_text(cmd, encoding="utf-8")
            self.copy_from_here(source=cmd_path, target=None)
            uv_cmd = f"""{UV_RUN_CMD} --with {MACHINECONFIG_VERSION} python {cmd_path.relative_to(Path.home())}"""
            return self.run(cmd=uv_cmd, desc=desc or f"run_py on {self.get_remote_repr()}", verbose=verbose, strict_err=strict_err, strict_returncode=strict_returncode)
        
        assert "obj=" in cmd, "The command sent to run_py must have `obj=` statement if return_obj is set to True"
        return_path = cmd_path.parent.joinpath(f"return_obj_{randstr()}.pkl")
        
        def func(pkl_path_rel2_home: str) -> None:
            from pathlib import Path
            import pickle
            pickle_path_obj = Path.home().joinpath(pkl_path_rel2_home).expanduser().absolute()
            obj = globals().get("obj", None)
            pickle_path_obj.write_bytes(pickle.dumps(obj))
        
        from machineconfig.utils.meta import function_to_script
        cmd_complement = function_to_script(func=func, call_with_kwargs={"pkl_path_rel2_home": return_path.relative_to(Path.home()).as_posix()})
        cmd_total = f"""{cmd}
{cmd_complement}
"""
        cmd_path.write_text(cmd_total, encoding="utf-8")
        self.copy_from_here(source=cmd_path, target=None)
        uv_cmd = f"""{UV_RUN_CMD} --with {MACHINECONFIG_VERSION} python {cmd_path.relative_to(Path.home())}"""
        _resp = self.run(uv_cmd, desc=desc, verbose=verbose, strict_err=True, strict_returncode=True).op.split("\n")[-1]
        res = self.copy_to_here(source=return_path, target=return_path)
        
        import pickle
        if isinstance(res, list):
            return pickle.loads(res[0].read_bytes())
        return pickle.loads(res.read_bytes())

    def copy_from_here(self, source: Union[str, Path], target: Optional[Union[str, Path]], z: bool = False, r: bool = False, overwrite: bool = False) -> Union[Path, list[Path]]:
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
        
        source_obj = Path(source).expanduser().absolute()
        if not source_obj.exists():
            raise RuntimeError(f"SSH Error: source `{source_obj}` does not exist!")
        
        if target is None:
            try:
                target_path = source_obj.relative_to(Path.home())
                target = Path("~") / target_path
            except ValueError:
                raise RuntimeError(f"If target is not specified, source must be relative to home directory, but got: {source_obj}")
            if z:
                target = Path(str(target) + ".zip")
        
        if not z and source_obj.is_dir():
            if not r:
                raise RuntimeError(f"SSH Error: source `{source_obj}` is a directory! Set `r=True` for recursive sending or `z=True` to zip it first.")
            
            source_list: list[Path] = [p for p in source_obj.rglob("*") if p.is_file()]
            remote_root = self._create_remote_target_dir(target_path=target, overwrite=overwrite)
            
            for idx, item in enumerate(source_list):
                print(f"   {idx + 1:03d}. {item}")
            for item in source_list:
                item_target = Path(remote_root).joinpath(item.relative_to(source_obj))
                self.copy_from_here(source=item, target=item_target, z=False, r=False, overwrite=overwrite)
            return source_list
        
        if z:
            print("🗜️ ZIPPING ...")
            import shutil
            zip_path = Path(str(source_obj) + "_archive")
            if source_obj.is_dir():
                shutil.make_archive(str(zip_path), "zip", source_obj)
            else:
                shutil.make_archive(str(zip_path), "zip", source_obj.parent, source_obj.name)
            source_obj = Path(str(zip_path) + ".zip")
        
        remotepath_str = self._create_remote_target_dir(target_path=target, overwrite=overwrite)
        remotepath = Path(remotepath_str)
        
        print(f"""📤 [SFTP UPLOAD] Sending file: {repr(source_obj)}  ==>  Remote Path: {remotepath.as_posix()}""")
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            if self.sftp is None:  # type: ignore[unreachable]
                raise RuntimeError(f"SFTP connection lost for {self.hostname}")
            self.sftp.put(localpath=str(source_obj), remotepath=remotepath.as_posix(), callback=pbar.view_bar)  # type: ignore
        
        if z:
            def func_unzip(item: str, overwrite: bool) -> None:
                from pathlib import Path
                import shutil
                import zipfile
                zip_path = Path(item).expanduser()
                extract_to = zip_path.parent / zip_path.stem
                if overwrite and extract_to.exists():
                    shutil.rmtree(extract_to)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_to)
                zip_path.unlink()
            
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=func_unzip, call_with_kwargs={"item": remotepath.as_posix(), "overwrite": overwrite})
            _resp = self.run_py(command, desc=f"UNZIPPING {remotepath.as_posix()}", return_obj=False, verbose=False, strict_err=True, strict_returncode=True)
            source_obj.unlink()
            print("\n")
        
        return source_obj

    def _check_remote_is_dir(self, source_path: Union[str, Path]) -> bool:
        """Helper to check if a remote path is a directory."""
        def check_is_dir(source_path: str) -> bool:
            from pathlib import Path
            return Path(source_path).expanduser().absolute().is_dir()
        
        from machineconfig.utils.meta import function_to_script
        command = function_to_script(func=check_is_dir, call_with_kwargs={"source_path": str(source_path)})
        result = self.run_py(cmd=command, desc=f"Check if source `{source_path}` is a dir", return_obj=True, verbose=False)
        assert isinstance(result, bool), f"Failed to check if {source_path} is directory"
        return result

    def _expand_remote_path(self, source_path: Union[str, Path]) -> str:
        """Helper to expand a path on the remote machine."""
        def expand_source(source_path: str) -> str:
            from pathlib import Path
            obj = Path(source_path).expanduser().absolute().as_posix()
            return obj
        
        from machineconfig.utils.meta import function_to_script
        command = function_to_script(func=expand_source, call_with_kwargs={"source_path": str(source_path)})
        result = self.run_py(cmd=command, desc="Resolving source path by expanding user", return_obj=True, verbose=False)
        assert isinstance(result, str), f"Could not resolve source path {source_path}"
        return result

    def copy_to_here(self, source: Union[str, Path], target: Optional[Union[str, Path]], z: bool = False, r: bool = False, init: bool = True) -> Union[Path, list[Path]]:
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}. Cannot transfer files.")
        
        if init:
            print(f"{'⬇️' * 5} SFTP DOWNLOADING FROM `{source}` TO `{target}`")
        
        source_obj = Path(source)
        
        if not z:
            is_dir = self._check_remote_is_dir(source_path=source_obj)
            
            if is_dir:
                if not r:
                    raise RuntimeError(f"SSH Error: source `{source_obj}` is a directory! Set r=True for recursive transfer or z=True to zip it.")
                
                def search_files(source_path: str) -> list[str]:
                    from pathlib import Path
                    obj = [item.as_posix() for item in Path(source_path).expanduser().absolute().rglob("*") if item.is_file()]
                    return obj
                
                from machineconfig.utils.meta import function_to_script
                command = function_to_script(func=search_files, call_with_kwargs={"source_path": source_obj.as_posix()})
                source_list_str = self.run_py(cmd=command, desc="Searching for files in source", return_obj=True, verbose=False)
                assert isinstance(source_list_str, list), f"Could not resolve source path {source}"
                source_list = [Path(item) for item in source_list_str]
                
                for idx, item in enumerate(source_list):
                    print(f"   {idx + 1:03d}. {item}")
                
                results: list[Path] = []
                for item in source_list:
                    item_target = Path(target).joinpath(item.relative_to(source_obj)) if target else None
                    result = self.copy_to_here(source=item, target=item_target, z=False, r=False, init=False)
                    if isinstance(result, Path):
                        results.append(result)
                    else:
                        results.extend(result)
                return results
        
        if z:
            print("🗜️ ZIPPING ...")
            def zip_source(source_path: str) -> str:
                from pathlib import Path
                import shutil
                src = Path(source_path).expanduser().absolute()
                zip_base = src.parent / (src.name + "_archive")
                if src.is_dir():
                    shutil.make_archive(str(zip_base), "zip", src)
                else:
                    shutil.make_archive(str(zip_base), "zip", src.parent, src.name)
                obj = str(zip_base) + ".zip"
                return obj
            
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=zip_source, call_with_kwargs={"source_path": source_obj.as_posix()})
            zipped_path = self.run_py(cmd=command, desc=f"Zipping source file {source}", return_obj=True, verbose=False)
            assert isinstance(zipped_path, str), f"Could not zip {source}"
            source_obj = Path(zipped_path)
        
        if target is None:
            def collapse_to_home(source_path: str) -> str:
                from pathlib import Path
                src = Path(source_path).expanduser().absolute()
                try:
                    rel = src.relative_to(Path.home())
                    obj = (Path("~") / rel).as_posix()
                    return obj
                except ValueError:
                    raise RuntimeError(f"Source path must be relative to home directory: {src}")
            
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=collapse_to_home, call_with_kwargs={"source_path": source_obj.as_posix()})
            target_str = self.run_py(cmd=command, desc="Finding default target via relative source path", return_obj=True, verbose=False)
            assert isinstance(target_str, str), "Could not resolve target path"
            target = Path(target_str)
            assert str(target).startswith("~"), f"If target is not specified, source must be relative to home.\n{target=}"
        
        target_obj = Path(target).expanduser().absolute()
        target_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if z and ".zip" not in target_obj.suffix:
            target_obj = target_obj.with_suffix(target_obj.suffix + ".zip")
        
        remote_source = self._expand_remote_path(source_path=source_obj)
        
        print(f"""📥 [DOWNLOAD] Receiving: {remote_source}  ==>  Local Path: {target_obj}""")
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            if self.sftp is None:  # type: ignore[unreachable]
                raise RuntimeError(f"SFTP connection lost for {self.hostname}")
            self.sftp.get(remotepath=remote_source, localpath=str(target_obj), callback=pbar.view_bar)  # type: ignore
        
        if z:
            import zipfile
            extract_to = target_obj.parent / target_obj.stem
            with zipfile.ZipFile(target_obj, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            target_obj.unlink()
            target_obj = extract_to
            
            def delete_temp_zip(source_path: str) -> None:
                from pathlib import Path
                import shutil
                path = Path(source_path)
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            
            from machineconfig.utils.meta import function_to_script
            command = function_to_script(func=delete_temp_zip, call_with_kwargs={"source_path": remote_source})
            self.run_py(cmd=command, desc="Cleaning temp zip files @ remote.", return_obj=False, verbose=False, strict_returncode=True, strict_err=True)
        
        print("\n")
        return target_obj

