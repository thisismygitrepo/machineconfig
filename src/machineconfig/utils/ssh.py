from typing import Callable, Optional, Any, cast, Union, Literal
import os
from pathlib import Path
import platform
from machineconfig.scripts.python.helpers.helpers_utils.python import MachineSpecs
from machineconfig.utils.code import get_uv_command
import rich.console
from machineconfig.utils.terminal import Response
from machineconfig.utils.accessories import pprint, randstr
from machineconfig.utils.meta import lambda_to_python_script
from machineconfig.utils.ssh_utils.abc import DEFAULT_PICKLE_SUBDIR


class SSH:
    @staticmethod
    def from_config_file(host: str) -> "SSH":
        return SSH(host=host, username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=False)

    def __init__(
        self,
        host: Optional[str],
        username: Optional[str],
        hostname: Optional[str],
        ssh_key_path: Optional[str],
        password: Optional[str],
        port: int,
        enable_compression: bool,
    ):
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
                assert "@" in host or ":" in host, (
                    f"Host must be in the form of `username@hostname:port` or `username@hostname` or `hostname:port`, but it is: {host}"
                )
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
        pprint(
            dict(host=self.host, hostname=self.hostname, username=self.username, password="***", port=self.port, key_filename=self.ssh_key_path),
            title="SSHing To",
        )
        sock = paramiko.ProxyCommand(self.proxycommand) if self.proxycommand is not None else None
        try:
            if password is None:
                allow_agent = True
                look_for_keys = True
            else:
                allow_agent = False
                look_for_keys = False
            self.ssh.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                key_filename=self.ssh_key_path,
                compress=self.enable_compression,
                sock=sock,
                allow_agent=allow_agent,
                look_for_keys=look_for_keys,
            )  # type: ignore
        except Exception as _err:
            rich.console.Console().print_exception()
            self.password = getpass.getpass(f"Enter password for {self.username}@{self.hostname}: ")
            self.ssh.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                key_filename=self.ssh_key_path,
                compress=self.enable_compression,
                sock=sock,
                allow_agent=False,
                look_for_keys=False,
            )  # type: ignore
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
                self.progress = Progress(
                    SpinnerColumn(), TextColumn("[bold blue]{task.description}"), BarColumn(), FileSizeColumn(), TransferSpeedColumn()
                )
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
        from machineconfig.scripts.python.helpers.helpers_utils.python import get_machine_specs

        self.local_specs: MachineSpecs = get_machine_specs()
        resp = self.run_shell_cmd_on_remote(
            command="""~/.local/bin/utils get-machine-specs """,
            verbose_output=False,
            description="Getting remote machine specs",
            strict_stderr=False,
            strict_return_code=False,
        )
        json_str = resp.op
        import ast

        self.remote_specs: MachineSpecs = cast(MachineSpecs, ast.literal_eval(json_str))
        self.terminal_responses: list[Response] = []

        from rich import inspect

        # local_info = dict(distro=self.local_specs.get("distro"), system=self.local_specs.get("system"), home_dir=self.local_specs.get("home_dir"))
        # remote_info = dict(distro=self.remote_specs.get("distro"), system=self.remote_specs.get("system"), home_dir=self.remote_specs.get("home_dir"))

        console = rich.console.Console()

        from io import StringIO

        local_buffer = StringIO()
        remote_buffer = StringIO()
        local_console = rich.console.Console(file=local_buffer, width=40)
        remote_console = rich.console.Console(file=remote_buffer, width=40)
        inspect(
            type("LocalInfo", (object,), dict(self.local_specs))(),
            value=False,
            title="SSHing From",
            docs=False,
            dunder=False,
            sort=False,
            console=local_console,
        )
        inspect(
            type("RemoteInfo", (object,), dict(self.remote_specs))(),
            value=False,
            title="SSHing To",
            docs=False,
            dunder=False,
            sort=False,
            console=remote_console,
        )
        local_lines = local_buffer.getvalue().split("\n")
        remote_lines = remote_buffer.getvalue().split("\n")
        max_lines = max(len(local_lines), len(remote_lines))
        for i in range(max_lines):
            left = local_lines[i] if i < len(local_lines) else ""
            right = remote_lines[i] if i < len(remote_lines) else ""
            console.print(f"{left:<50} {right}")

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
        return self.run_shell_cmd_on_remote(
            command="Restart-Computer -Force" if self.remote_specs["system"] == "Windows" else "sudo reboot",
            verbose_output=True,
            description="",
            strict_stderr=False,
            strict_return_code=False,
        )

    def send_ssh_key(self) -> Response:
        self.copy_from_here(source_path="~/.ssh/id_rsa.pub", target_rel2home=None, compress_with_zip=False, recursive=False, overwrite_existing=False)
        if self.remote_specs["system"] != "Windows":
            raise RuntimeError("send_ssh_key is only supported for Windows remote machines")
        python_code = '''
from pathlib import Path
import subprocess
sshd_dir = Path("C:/ProgramData/ssh")
admin_auth_keys = sshd_dir / "administrators_authorized_keys"
sshd_config = sshd_dir / "sshd_config"
pubkey_path = Path.home() / ".ssh" / "id_rsa.pub"
key_content = pubkey_path.read_text(encoding="utf-8").strip()
if admin_auth_keys.exists():
    existing = admin_auth_keys.read_text(encoding="utf-8")
    if not existing.endswith("\\n"):
        existing += "\\n"
    admin_auth_keys.write_text(existing + key_content + "\\n", encoding="utf-8")
else:
    admin_auth_keys.write_text(key_content + "\\n", encoding="utf-8")
icacls_cmd = f'icacls "{admin_auth_keys}" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"'
subprocess.run(icacls_cmd, shell=True, check=True)
if sshd_config.exists():
    config_text = sshd_config.read_text(encoding="utf-8")
    config_text = config_text.replace("#PubkeyAuthentication", "PubkeyAuthentication")
    sshd_config.write_text(config_text, encoding="utf-8")
subprocess.run("Restart-Service sshd -Force", shell=True, check=True)
print("SSH key added successfully")
'''
        return self.run_py_remotely(python_code=python_code, uv_with=None, uv_project_dir=None, description="Adding SSH key to Windows remote", verbose_output=True, strict_stderr=False, strict_return_code=False)

    def get_remote_repr(self, add_machine: bool = False) -> str:
        return f"{self.username}@{self.hostname}:{self.port}" + (
            f" [{self.remote_specs['system']}][{self.remote_specs['distro']}]" if add_machine else ""
        )

    def get_local_repr(self, add_machine: bool = False) -> str:
        import getpass

        return f"{getpass.getuser()}@{platform.node()}" + (f" [{platform.system()}][{self.local_specs['distro']}]" if add_machine else "")

    def get_ssh_conn_str(self, command: str) -> str:
        return (
            "ssh "
            + (f" -i {self.ssh_key_path}" if self.ssh_key_path else "")
            + self.get_remote_repr(add_machine=False).replace(":", " -p ")
            + (f" -t {command} " if command != "" else " ")
        )

    def __repr__(self) -> str:
        return f"local {self.get_local_repr(add_machine=True)} >>> SSH TO >>> remote {self.get_remote_repr(add_machine=True)}"

    def run_shell_cmd_on_local(self, command: str) -> Response:
        print(f"""💻 [LOCAL EXECUTION] Running command on node: {self.local_specs["system"]} Command: {command}""")
        res = Response(cmd=command)
        res.output.returncode = os.system(command)
        return res

    def run_shell_cmd_on_remote(
        self, command: str, verbose_output: bool, description: str, strict_stderr: bool, strict_return_code: bool
    ) -> Response:
        raw = self.ssh.exec_command(command)
        res = Response(stdin=raw[0], stdout=raw[1], stderr=raw[2], cmd=command, desc=description)  # type: ignore
        if verbose_output:
            res.print()
        else:
            res.capture().print_if_unsuccessful(
                desc=description, strict_err=strict_stderr, strict_returncode=strict_return_code, assert_success=False
            )
        # self.terminal_responses.append(res)
        return res

    def _run_py_prep(self, python_code: str, uv_with: Optional[list[str]], uv_project_dir: Optional[str], on: Literal["local", "remote"]) -> str:
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
        match on:
            case "local":
                uv_cmd = get_uv_command(platform=self.local_specs["system"])
            case "remote":
                uv_cmd = get_uv_command(platform=self.remote_specs["system"])
            case _:
                raise ValueError(f"Invalid value for 'on': {on}. Must be 'local' or 'remote'")
        uv_cmd = f"""{uv_cmd} run {with_clause} python {py_path.relative_to(Path.home())}"""
        return uv_cmd

    def run_py_remotely(
        self,
        python_code: str,
        uv_with: Optional[list[str]],
        uv_project_dir: Optional[str],
        description: str,
        verbose_output: bool,
        strict_stderr: bool,
        strict_return_code: bool,
    ) -> Response:
        uv_cmd = self._run_py_prep(python_code=python_code, uv_with=uv_with, uv_project_dir=uv_project_dir, on="remote")
        return self.run_shell_cmd_on_remote(
            command=uv_cmd,
            verbose_output=verbose_output,
            description=description or f"run_py on {self.get_remote_repr(add_machine=False)}",
            strict_stderr=strict_stderr,
            strict_return_code=strict_return_code,
        )

    def run_lambda_function(self, func: Callable[..., Any], import_module: bool, uv_with: Optional[list[str]], uv_project_dir: Optional[str]):
        command = lambda_to_python_script(func, in_global=True, import_module=import_module)
        # turns ou that the code below for some reason runs but zellij doesn't start, looks like things are assigned to different user.
        # return self.run_py(python_code=command, uv_with=uv_with, uv_project_dir=uv_project_dir,
        #                    description=f"run_py_func {func.__name__} on {self.get_remote_repr(add_machine=False)}",
        #                    verbose_output=True, strict_stderr=True, strict_return_code=True)
        uv_cmd = self._run_py_prep(python_code=command, uv_with=uv_with, uv_project_dir=uv_project_dir, on="remote")
        if self.remote_specs["system"] == "Linux":
            uv_cmd_modified = f'bash -l -c "{uv_cmd}"'
        else:
            uv_cmd_modified = uv_cmd
        # This works even withou the modified uv cmd:
        # from machineconfig.utils.code import run_shell_script
        # assert self.host is not None, "SSH host must be specified to run remote commands"
        # process = run_shell_script(f"ssh {self.host} -n '. ~/.profile; . ~/.bashrc; {uv_cmd}'")
        # return process
        return self.run_shell_cmd_on_remote(
            command=uv_cmd_modified,
            verbose_output=True,
            description=f"run_py_func {func.__name__} on {self.get_remote_repr(add_machine=False)}",
            strict_stderr=True,
            strict_return_code=True,
        )

    def simple_sftp_get(self, remote_path: str, local_path: Path) -> None:
        """Simple SFTP get without any recursion or path expansion - for internal use only."""
        if self.sftp is None:
            raise RuntimeError(f"SFTP connection not available for {self.hostname}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(remotepath=remote_path, localpath=str(local_path))

    def create_parent_dir_and_check_if_exists(self, path_rel2home: str, overwrite_existing: bool) -> None:
        from machineconfig.utils.ssh_utils.utils import create_dir_and_check_if_exists

        return create_dir_and_check_if_exists(self, path_rel2home=path_rel2home, overwrite_existing=overwrite_existing)

    def check_remote_is_dir(self, source_path: Union[str, Path]) -> bool:
        from machineconfig.utils.ssh_utils.utils import check_remote_is_dir

        return check_remote_is_dir(self, source_path=source_path)

    def expand_remote_path(self, source_path: Union[str, Path]) -> str:
        from machineconfig.utils.ssh_utils.utils import expand_remote_path

        return expand_remote_path(self, source_path=source_path)

    def copy_from_here(
        self, source_path: str, target_rel2home: Optional[str], compress_with_zip: bool, recursive: bool, overwrite_existing: bool
    ) -> None:
        from machineconfig.utils.ssh_utils.copy_from_here import copy_from_here

        return copy_from_here(
            self,
            source_path=source_path,
            target_rel2home=target_rel2home,
            compress_with_zip=compress_with_zip,
            recursive=recursive,
            overwrite_existing=overwrite_existing,
        )

    def copy_to_here(
        self, source: Union[str, Path], target: Optional[Union[str, Path]], compress_with_zip: bool, recursive: bool, internal_call: bool = False
    ) -> None:
        from machineconfig.utils.ssh_utils.copy_to_here import copy_to_here

        return copy_to_here(self, source=source, target=target, compress_with_zip=compress_with_zip, recursive=recursive, internal_call=internal_call)


if __name__ == "__main__":
    ssh = SSH(host="p51s", username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=False)
