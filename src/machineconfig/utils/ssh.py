from typing import Optional, Any, Union, List
import os
from dataclasses import dataclass
import rich.console
from machineconfig.utils.terminal import Terminal, Response, MACHINE
from machineconfig.utils.path_reduced import PathExtended, PLike, OPLike
from machineconfig.utils.utils2 import pprint
# from machineconfig.utils.ve import get_ve_activate_line


@dataclass
class Scout:
    source_full: PathExtended
    source_rel2home: PathExtended
    exists: bool
    is_dir: bool
    files: Optional[List[PathExtended]]


def scout(source: PLike, z: bool = False, r: bool = False) -> Scout:
    source_full = PathExtended(source).expanduser().absolute()
    source_rel2home = source_full.collapseuser()
    exists = source_full.exists()
    is_dir = source_full.is_dir() if exists else False
    if z and exists:
        try:
            source_full = source_full.zip()
        except Exception as ex:
            raise Exception(f"Could not zip {source_full} due to {ex}") from ex  # type: ignore # pylint: disable=W0719
        source_rel2home = source_full.zip()
    if r and exists and is_dir:
        files = [item.collapseuser() for item in source_full.search(folders=False, r=True)]
    else:
        files = None
    return Scout(source_full=source_full, source_rel2home=source_rel2home, exists=exists, is_dir=is_dir, files=files)


class SSH:  # inferior alternative: https://github.com/fabric/fabric
    def __init__(
        self, host: Optional[str] = None, username: Optional[str] = None, hostname: Optional[str] = None, sshkey: Optional[str] = None, pwd: Optional[str] = None, port: int = 22, ve: Optional[str] = ".venv", compress: bool = False
    ):  # https://stackoverflow.com/questions/51027192/execute-command-script-using-different-shell-in-ssh-paramiko
        self.pwd = pwd
        self.ve = ve
        self.compress = compress  # Defaults: (1) use localhost if nothing provided.

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

                config = pconfig.SSHConfig.from_path(str(PathExtended.home().joinpath(".ssh/config")))
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

        self.sshkey = str(PathExtended(sshkey).expanduser().absolute()) if sshkey is not None else None  # no need to pass sshkey if it was configured properly already
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pprint(dict(host=self.host, hostname=self.hostname, username=self.username, password="***", port=self.port, key_filename=self.sshkey, ve=self.ve), title="SSHing To")
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
            print(f"""⚠️  WARNING: Failed to open SFTP connection to {hostname}.
   Error Details: {err}\nData transfer may be affected!""")

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

    def get_remote_machine(self) -> MACHINE:
        if self._remote_machine is None:
            if self.run("$env:OS", verbose=False, desc="Testing Remote OS Type").op == "Windows_NT" or self.run("echo %OS%", verbose=False, desc="Testing Remote OS Type Again").op == "Windows_NT":
                self._remote_machine = "Windows"
            else:
                self._remote_machine = "Linux"
        return self._remote_machine  # echo %OS% TODO: uname on linux

    def get_local_distro(self) -> str:
        if self._local_distro is None:
            command = """uv run --with distro python -c "import distro; print(distro.name(pretty=True))" """
            import subprocess

            res = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()
            self._local_distro = res
            return res
        return self._local_distro

    def get_remote_distro(self):
        if self._remote_distro is None:
            res = self.run("""~/.local/bin/uv run --with distro python -c "import distro; print(distro.name(pretty=True))" """)
            self._remote_distro = res.op_if_successfull_or_default() or ""
        return self._remote_distro

    def restart_computer(self):
        self.run("Restart-Computer -Force" if self.get_remote_machine() == "Windows" else "sudo reboot")

    def send_ssh_key(self):
        self.copy_from_here("~/.ssh/id_rsa.pub")
        assert self.get_remote_machine() == "Windows"
        code_url = "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1"
        code = PathExtended(code_url).download().read_text(encoding="utf-8")
        self.run(code)

    def copy_env_var(self, name: str):
        assert self.get_remote_machine() == "Linux"
        return self.run(f"{name} = {os.environ[name]}; export {name}")

    def get_remote_repr(self, add_machine: bool = False) -> str:
        return f"{self.username}@{self.hostname}:{self.port}" + (f" [{self.get_remote_machine()}][{self.get_remote_distro()}]" if add_machine else "")

    def get_local_repr(self, add_machine: bool = False) -> str:
        import getpass

        return f"{getpass.getuser()}@{self.platform.node()}" + (f" [{self.platform.system()}][{self.get_local_distro()}]" if add_machine else "")

    def __repr__(self):
        return f"local {self.get_local_repr(add_machine=True)} >>> SSH TO >>> remote {self.get_remote_repr(add_machine=True)}"

    def run_locally(self, command: str):
        print(f"""💻 [LOCAL EXECUTION] Running command on node: {self.platform.node()} Command: {command}""")
        res = Response(cmd=command)
        res.output.returncode = os.system(command)
        return res

    def get_ssh_conn_str(self, cmd: str = ""):
        return "ssh " + (f" -i {self.sshkey}" if self.sshkey else "") + self.get_remote_repr().replace(":", " -p ") + (f" -t {cmd} " if cmd != "" else " ")

    def run(self, cmd: str, verbose: bool = True, desc: str = "", strict_err: bool = False, strict_returncode: bool = False) -> Response:
        raw = self.ssh.exec_command(cmd)
        res = Response(stdin=raw[0], stdout=raw[1], stderr=raw[2], cmd=cmd, desc=desc)  # type: ignore
        if not verbose:
            res.capture().print_if_unsuccessful(desc=desc, strict_err=strict_err, strict_returncode=strict_returncode, assert_success=False)
        else:
            res.print()
        self.terminal_responses.append(res)
        return res

    def run_py(self, cmd: str, desc: str = "", return_obj: bool = False, verbose: bool = True, strict_err: bool = False, strict_returncode: bool = False) -> Union[Any, Response]:
        assert '"' not in cmd, 'Avoid using `"` in your command. I dont know how to handle this when passing is as command to python in pwsh command.'
        if not return_obj:
            return self.run(
                cmd=f"""uv run --no-dev --project $HOME/code/machineconfig -c "{Terminal.get_header(wdir=None, toolbox=True)}{cmd}\n""" + '"',
                desc=desc or f"run_py on {self.get_remote_repr()}",
                verbose=verbose,
                strict_err=strict_err,
                strict_returncode=strict_returncode,
            )
        assert "obj=" in cmd, "The command sent to run_py must have `obj=` statement if return_obj is set to True"
        source_file = self.run_py(f"""{cmd}\npath = Save.pickle(obj=obj, path=P.tmpfile(suffix='.pkl'))\nprint(path)""", desc=desc, verbose=verbose, strict_err=True, strict_returncode=True).op.split("\n")[-1]
        res = self.copy_to_here(source=source_file, target=PathExtended.tmpfile(suffix=".pkl"))
        import pickle

        return pickle.loads(res.read_bytes())

    def copy_from_here(self, source: PLike, target: OPLike = None, z: bool = False, r: bool = False, overwrite: bool = False, init: bool = True) -> Union[PathExtended, list[PathExtended]]:
        if init:
            print(f"{'⬆️' * 5} [SFTP UPLOAD] FROM `{source}` TO `{target}`")  # TODO: using return_obj do all tests required in one go.
        source_obj = PathExtended(source).expanduser().absolute()
        if not source_obj.exists():
            raise RuntimeError(f"Meta.SSH Error: source `{source_obj}` does not exist!")
        if target is None:
            target = PathExtended(source_obj).expanduser().absolute().collapseuser(strict=True)
            assert target.is_relative_to("~"), "If target is not specified, source must be relative to home."
            if z:
                target += ".zip"
        if not z and source_obj.is_dir():
            if r is False:
                raise RuntimeError(f"Meta.SSH Error: source `{source_obj}` is a directory! either set `r=True` for recursive sending or raise `z=True` flag to zip it first.")
            source_list: list[PathExtended] = source_obj.search("*", folders=False, files=True, r=True)
            remote_root = (
                self.run_py(
                    f"path=P(r'{PathExtended(target).as_posix()}').expanduser()\n{'path.delete(sure=True)' if overwrite else ''}\nprint(path.create())",
                    desc=f"Creating Target directory `{PathExtended(target).as_posix()}` @ {self.get_remote_repr()}",
                    verbose=False,
                ).op
                or ""
            )
            for idx, item in enumerate(source_list):
                print(f"   {idx + 1:03d}. {item}")
            for item in source_list:
                a__target = PathExtended(remote_root).joinpath(item.relative_to(source_obj))
                self.copy_from_here(source=item, target=a__target)
            return list(source_list)
        if z:
            print("🗜️ ZIPPING ...")
            source_obj = PathExtended(source_obj).expanduser().zip(content=True)  # .append(f"_{randstr()}", inplace=True)  # eventually, unzip will raise content flag, so this name doesn't matter.
        remotepath = (
            self.run_py(
                f"path=P(r'{PathExtended(target).as_posix()}').expanduser()\n{'path.delete(sure=True)' if overwrite else ''}\nprint(path.parent.create())",
                desc=f"Creating Target directory `{PathExtended(target).parent.as_posix()}` @ {self.get_remote_repr()}",
                verbose=False,
            ).op
            or ""
        )
        remotepath = PathExtended(remotepath.split("\n")[-1]).joinpath(PathExtended(target).name)
        print(f"""📤 [SFTP UPLOAD] Sending file: {repr(PathExtended(source_obj))}  ==>  Remote Path: {remotepath.as_posix()}""")
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            self.sftp.put(localpath=PathExtended(source_obj).expanduser(), remotepath=remotepath.as_posix(), callback=pbar.view_bar)  # type: ignore # pylint: disable=E1129
        if z:
            _resp = self.run_py(f"""P(r'{remotepath.as_posix()}').expanduser().unzip(content=False, inplace=True, overwrite={overwrite})""", desc=f"UNZIPPING {remotepath.as_posix()}", verbose=False, strict_err=True, strict_returncode=True)
            source_obj.delete(sure=True)
            print("\n")
        return source_obj

    def copy_to_here(self, source: PLike, target: OPLike = None, z: bool = False, r: bool = False, init: bool = True) -> PathExtended:
        if init:
            print(f"{'⬇️' * 5} SFTP DOWNLOADING FROM `{source}` TO `{target}`")
        if not z and self.run_py(f"print(P(r'{source}').expanduser().absolute().is_dir())", desc=f"Check if source `{source}` is a dir", verbose=False, strict_returncode=True, strict_err=True).op.split("\n")[-1] == "True":
            if r is False:
                raise RuntimeError(f"source `{source}` is a directory! either set r=True for recursive sending or raise zip_first flag.")
            source_list = self.run_py(f"obj=P(r'{source}').search(folders=False, r=True).collapseuser(strict=False)", desc="Searching for files in source", return_obj=True, verbose=False)
            assert isinstance(source_list, List), f"Could not resolve source path {source} due to error"
            for file in source_list:
                self.copy_to_here(source=file.as_posix(), target=PathExtended(target).joinpath(PathExtended(file).relative_to(source)) if target else None, r=False)
        if z:
            tmp: Response = self.run_py(f"print(P(r'{source}').expanduser().zip(inplace=False, verbose=False))", desc=f"Zipping source file {source}", verbose=False)
            tmp2 = tmp.op2path(strict_returncode=True, strict_err=True)
            if not isinstance(tmp2, PathExtended):
                raise RuntimeError(f"Could not zip {source} due to {tmp.err}")
            else:
                source = tmp2
        if target is None:
            tmpx = self.run_py(f"print(P(r'{PathExtended(source).as_posix()}').collapseuser(strict=False).as_posix())", desc="Finding default target via relative source path", strict_returncode=True, strict_err=True, verbose=False).op2path()
            if isinstance(tmpx, PathExtended):
                target = tmpx
            else:
                raise RuntimeError(f"Could not resolve target path {target} due to error")
            assert target.is_relative_to("~"), f"If target is not specified, source must be relative to home.\n{target=}"
        target_obj = PathExtended(target).expanduser().absolute()
        target_obj.parent.mkdir(parents=True, exist_ok=True)
        if z and ".zip" not in target_obj.suffix:
            target_obj += ".zip"
        if "~" in str(source):
            tmp3 = self.run_py(f"print(P(r'{source}').expanduser())", desc="# Resolving source path address by expanding user", strict_returncode=True, strict_err=True, verbose=False).op2path()
            if isinstance(tmp3, PathExtended):
                source = tmp3
            else:
                raise RuntimeError(f"Could not resolve source path {source} due to")
        else:
            source = PathExtended(source)
        print(f"""📥 [DOWNLOAD] Receiving: {source}  ==>  Local Path: {target_obj}""")
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:  # type: ignore # pylint: disable=E1129
            assert self.sftp is not None, f"Could not establish SFTP connection to {self.hostname}."
            self.sftp.get(remotepath=source.as_posix(), localpath=str(target_obj), callback=pbar.view_bar)  # type: ignore
        if z:
            target_obj = target_obj.unzip(inplace=True, content=True)
            self.run_py(f"P(r'{source.as_posix()}').delete(sure=True)", desc="Cleaning temp zip files @ remote.", strict_returncode=True, strict_err=True, verbose=False)
        print("\n")
        return target_obj

    def receieve(self, source: PLike, target: OPLike = None, z: bool = False, r: bool = False) -> PathExtended:
        scout = self.run_py(cmd=f"obj=scout(r'{source}', z={z}, r={r})", desc=f"Scouting source `{source}` path on remote", return_obj=True, verbose=False)
        assert isinstance(scout, Scout)
        if not z and scout.is_dir and scout.files is not None:
            if r:
                tmp: list[PathExtended] = [self.receieve(source=file.as_posix(), target=PathExtended(target).joinpath(PathExtended(file).relative_to(source)) if target else None, r=False) for file in scout.files]
                return tmp[0]
            else:
                print("Source is a directory! either set `r=True` for recursive sending or raise `zip_first=True` flag.")
        if target:
            target = PathExtended(target).expanduser().absolute()
        else:
            target = scout.source_rel2home.expanduser().absolute()
        target.parent.mkdir(parents=True, exist_ok=True)
        if z and ".zip" not in target.suffix:
            target += ".zip"
        source = scout.source_full
        with self.tqdm_wrap(ascii=True, unit="b", unit_scale=True) as pbar:
            self.sftp.get(remotepath=source.as_posix(), localpath=target.as_posix(), callback=pbar.view_bar)  # type: ignore # pylint: disable=E1129
        if z:
            target = target.unzip(inplace=True, content=True)
            self.run_py(f"P(r'{source.as_posix()}').delete(sure=True)", desc="Cleaning temp zip files @ remote.", strict_returncode=True, strict_err=True)
        print("\n")
        return target

    # def print_summary(self):
    #     import polars as pl
    #     df = pl.DataFrame(List(self.terminal_responses).apply(lambda rsp: dict(desc=rsp.desc, err=rsp.err, returncode=rsp.returncode)).list)
    #     print("\nSummary of operations performed:")
    #     print(df.to_pandas().to_markdown())
    #     if ((df.select('returncode').to_series().to_list()[2:] == [None] * (len(df) - 2)) and (df.select('err').to_series().to_list()[2:] == [''] * (len(df) - 2))): print("\nAll operations completed successfully.\n")
    #     else: print("\nSome operations failed. \n")
    #     return df
