from machineconfig.utils.path_extended import PathExtended
import subprocess
from typing import Any, BinaryIO, Optional, Union
from typing import Literal, TypeAlias
from dataclasses import dataclass


SHELLS: TypeAlias = Literal["default", "cmd", "powershell", "pwsh", "bash"]  # pwsh.exe is PowerShell (community) and powershell.exe is Windows Powershell (msft)
CONSOLE: TypeAlias = Literal["wt", "cmd"]
MACHINE: TypeAlias = Literal["Windows", "Linux", "Darwin"]


@dataclass
class STD:
    stdin: str
    stdout: str
    stderr: str
    returncode: int


class Response:
    @staticmethod
    def from_completed_process(cp: subprocess.CompletedProcess[str]):
        resp = Response(cmd=cp.args)
        resp.output.stdout = cp.stdout
        resp.output.stderr = cp.stderr
        resp.output.returncode = cp.returncode
        return resp

    def __init__(self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None, stderr: Optional[BinaryIO] = None, cmd: Optional[str] = None, desc: str = ""):
        self.std = dict(stdin=stdin, stdout=stdout, stderr=stderr)
        self.output = STD(stdin="", stdout="", stderr="", returncode=0)
        self.input = cmd
        self.desc = desc  # input command

    def __call__(self, *args: Any, **kwargs: Any) -> Optional[str]:
        _ = args, kwargs
        return self.op.rstrip() if type(self.op) is str else None
    def __repr__(self) -> str:
        return f"Response({self.input=}, {self.output=}, {self.desc=}, {self.op=}, {self.ip=}, {self.err=}, {self.returncode=})"
    @property
    def op(self) -> str:
        return self.output.stdout

    @property
    def ip(self) -> str:
        return self.output.stdin

    @property
    def err(self) -> str:
        return self.output.stderr

    @property
    def returncode(self) -> int:
        return self.output.returncode

    def op2path(self, strict_returncode: bool = True, strict_err: bool = False) -> Union[PathExtended, None]:
        if self.is_successful(strict_returcode=strict_returncode, strict_err=strict_err):
            return PathExtended(self.op.rstrip())
        return None

    def op_if_successfull_or_default(self, strict_returcode: bool = True, strict_err: bool = False) -> Optional[str]:
        return self.op if self.is_successful(strict_returcode=strict_returcode, strict_err=strict_err) else None

    def is_successful(self, strict_returcode: bool = True, strict_err: bool = False) -> bool:
        return ((self.returncode in {0, None}) if strict_returcode else True) and (self.err == "" if strict_err else True)

    def capture(self):
        for key in ["stdin", "stdout", "stderr"]:
            val: Optional[BinaryIO] = self.std[key]
            if val is not None and val.readable():
                self.output.__dict__[key] = val.read().decode().rstrip()
        return self

    def print_if_unsuccessful(self, desc: str = "TERMINAL CMD", strict_err: bool = False, strict_returncode: bool = False, assert_success: bool = False):
        success = self.is_successful(strict_err=strict_err, strict_returcode=strict_returncode)
        if assert_success:
            assert success, self.print(capture=False, desc=desc)
        if success:
            print(f"✅ {desc} completed successfully")
        else:
            self.print(capture=False, desc=desc)
        return self

    def print(self, desc: str = "TERMINAL CMD", capture: bool = True):
        if capture:
            self.capture()
        from rich import console

        con = console.Console()
        from rich.panel import Panel
        from rich.text import Text  # from rich.syntax import Syntax; syntax = Syntax(my_code, "python", theme="monokai", line_numbers=True)

        tmp1 = Text("📥 Input Command:\n")
        tmp1.stylize("u bold blue")
        tmp2 = Text("\n📤 Terminal Response:\n")
        tmp2.stylize("u bold blue")
        list_str = [f"{f' {idx} - {key} '}".center(40, "═") + f"\n{val}" for idx, (key, val) in enumerate(self.output.__dict__.items())]
        txt = tmp1 + Text(str(self.input), style="white") + tmp2 + Text("\n".join(list_str), style="white")
        con.print(Panel(txt, title=f"🖥️  {self.desc}", subtitle=f"📋 {desc}", width=150, style="bold cyan on black"))
        return self
