
"""SelfSSh
"""


from crocodile.file_management import PLike
from crocodile.meta import MACHINE, Terminal
from typing import Optional, Any
import getpass
import platform
import subprocess


class SelfSSH:
    """Instead of SSH'ing to the same machine, one can use this interface.
    """
    def __init__(self):
        self.hostname = "localhost"
        self._remote_machine: Optional[MACHINE] = None
        self.remote_env_cmd = ". activate_ve"
        self.sftp: Any
    def __getstate__(self) -> object: return {}
    def __setstate__(self, state: dict[str, Any]) -> None:
        """This behaviour makes SelfSSH dynamic, even if it was pickled from windows machine, when unpickled on Linux, it will behave as a Linux machine instance."""
        _ = state
        new_instance = SelfSSH()
        self.__dict__.update(new_instance.__dict__)
        return None
    def run(self, cmd: str, desc: str = "", verbose: bool = False):
        _ = desc, verbose
        return Terminal().run(cmd, shell="powershell")
    def run_py(self, cmd: str, verbose: bool = False, desc: str = ''):
        _ = verbose, cmd, desc
        exec(cmd)  # type: ignore # pylint: disable=exec-used
        return None
    def get_ssh_conn_str(self): return "ssh localhost"
    def get_remote_machine(self) -> MACHINE:
        if self._remote_machine is None:
            self._remote_machine = "Windows" if (self.run("$env:OS").op.rstrip("\n") == "Windows_NT" or self.run("echo %OS%").op == "Windows_NT") else "Linux"
        return self._remote_machine
    def get_remote_repr(self, add_machine: bool = False):
        _ = add_machine
        host = f"{getpass.getuser()}@{platform.node()}"
        return f"SelfSSH({host}) REMOTE"
    def get_local_repr(self, add_machine: bool = False): return self.get_remote_repr(add_machine=add_machine).replace("REMOTE", "LOCAL")
    def open_console(self, cmd: str = '', new_window: bool = True, terminal: Optional[str] = None, shell: str = "pwsh"):
        _ = cmd, shell, new_window, terminal
        # return Terminal().run_async("", new_window=True, shell=shell)
        # Terminal().run_async(*(self.get_ssh_conn_str(cmd=cmd).split(" ")), new_window=new_window, terminal=terminal, shell=shell)
        if platform.system() == "Windows":
            subprocess.Popen(["wt", "--profile", "pwsh"], stdin=subprocess.PIPE, shell=True)
        elif platform.system() == "Linux":
            subprocess.Popen(["zellij --session haha"], shell=True, stdin=None, stdout=None, stderr=None)
    def copy_to_here(self, source: PLike = '', target: Optional[str] = '', z: bool = True, r: bool = True, desc: str = '', overwrite: bool = False):
        _ = source, target, z, r, desc, overwrite
        return None
    def copy_from_here(self, source: PLike = '', target: Optional[str] = '', z: bool = True, r: bool = True, desc: str = '', overwrite: bool = False):
        _ = source, target, z, r, desc, overwrite
        return None
