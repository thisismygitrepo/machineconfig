from machineconfig.utils.path_reduced import PathExtended, OPLike
import subprocess
from typing import Any, BinaryIO, Optional, Union
import platform
import sys
import os
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


# DEPRECATED: Use subprocess.run directly instead of Terminal class.
# The Terminal class has been replaced with inline subprocess calls to underlying primitives.
# This file is kept for reference but should not be used.


class Terminal:
    def __init__(self, stdout: Optional[int] = subprocess.PIPE, stderr: Optional[int] = subprocess.PIPE, stdin: Optional[int] = subprocess.PIPE, elevated: bool = False):
        self.machine: str = platform.system()
        self.elevated: bool = elevated
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin

    # def set_std_system(self): self.stdout = sys.stdout; self.stderr = sys.stderr; self.stdin = sys.stdin
    def set_std_pipe(self):
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE
        self.stdin = subprocess.PIPE

    def set_std_null(self):
        self.stdout, self.stderr, self.stdin = subprocess.DEVNULL, subprocess.DEVNULL, subprocess.DEVNULL  # Equivalent to `echo 'foo' &> /dev/null`

    def run(self, *cmds: str, shell: Optional[SHELLS] = "default", check: bool = False, ip: Optional[str] = None) -> Response:  # Runs SYSTEM commands like subprocess.run
        """Blocking operation. Thus, if you start a shell via this method, it will run in the main and won't stop until you exit manually IF stdin is set to sys.stdin, otherwise it will run and close quickly. Other combinations of stdin, stdout can lead to funny behaviour like no output but accept input or opposite.
        * This method is short for: res = subprocess.run("powershell command", capture_output=True, shell=True, text=True) and unlike os.system(cmd), subprocess.run(cmd) gives much more control over the output and input.
        * `shell=True` loads up the profile of the shell called so more specific commands can be run. Importantly, on Windows, the `start` command becomes availalbe and new windows can be launched.
        * `capture_output` prevents the stdout to redirect to the stdout of the script automatically, instead it will be stored in the Response object returned. # `capture_output=True` same as `stdout=subprocess.PIPE, stderr=subprocess.PIPE`"""
        my_list = list(
            cmds
        )  # `subprocess.Popen` (process open) is the most general command. Used here to create asynchronous job. `subprocess.run` is a thin wrapper around Popen that makes it wait until it finishes the task. `suprocess.call` is an archaic command for pre-Python-3.5.
        if self.machine == "Windows" and shell in {"powershell", "pwsh"}:
            my_list = [shell, "-Command"] + my_list  # alternatively, one can run "cmd"
        if self.elevated is False or self.is_user_admin():
            resp: subprocess.CompletedProcess[str] = subprocess.run(my_list, stderr=self.stderr, stdin=self.stdin, stdout=self.stdout, text=True, shell=True, check=check, input=ip)
        else:
            resp = __import__("ctypes").windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return Response.from_completed_process(resp)

    def run_script(self, script: str, shell: SHELLS = "default", verbose: bool = False):
        if self.machine == "Linux":
            script = "#!/bin/bash" + "\n" + script  # `source` is only available in bash.
        script_file = PathExtended.tmpfile(name="tmp_shell_script", suffix=".ps1" if self.machine == "Windows" else ".sh", folder="tmp_scripts")
        script_file.write_text(script, newline={"Windows": None, "Linux": "\n"}[self.machine])
        if shell == "default":
            if self.machine == "Windows":
                start_cmd = "powershell"  # default shell on Windows is cmd which is not very useful. (./source is not available)
                full_command: Union[list[str], str] = [start_cmd, str(script_file)]  # shell=True will cause this to be a string anyway (with space separation)
            else:
                start_cmd = "bash"
                full_command = f"{start_cmd} {script_file}"  # full_command = [start_cmd, str(script_file)]
        else:
            full_command = f"{shell} {script_file}"  # full_command = [shell, str(tmp_file)]
        if verbose:
            desc = "Script to be executed:"
            if platform.system() == "Windows":
                lexer = "powershell"
            elif platform.system() == "Linux":
                lexer = "sh"
            elif platform.system() == "Darwin":
                lexer = "sh"  # macOS uses similar shell to Linux
            else:
                raise NotImplementedError(f"Platform {platform.system()} not supported.")
            from rich.console import Console
            from rich.panel import Panel
            from rich.syntax import Syntax
            import rich.progress as pb

            console = Console()
            console.print(Panel(Syntax(code=script, lexer=lexer), title=f"📄 {desc}"), style="bold red")
            with pb.Progress(transient=True) as progress:
                _task = progress.add_task(f"Running Script @ {script_file}", total=None)
                resp = subprocess.run(full_command, stderr=self.stderr, stdin=self.stdin, stdout=self.stdout, text=True, shell=True, check=False)
        else:
            resp = subprocess.run(full_command, stderr=self.stderr, stdin=self.stdin, stdout=self.stdout, text=True, shell=True, check=False)
        return Response.from_completed_process(resp)

    def run_py(self, script: str, wdir: OPLike = None, interactive: bool = True, ipython: bool = True, shell: Optional[str] = None, terminal: str = "", new_window: bool = True, header: bool = True):  # async run, since sync run is meaningless.
        script = (Terminal.get_header(wdir=wdir, toolbox=True) if header else "") + script + ("\nDisplayData.set_pandas_auto_width()\n" if terminal in {"wt", "powershell", "pwsh"} else "")
        py_script = PathExtended.tmpfile(name="tmp_python_script", suffix=".py", folder="tmp_scripts/terminal")
        py_script.write_text(f"""print(r'''{script}''')""" + "\n" + script)
        print(f"""🚀 [ASYNC PYTHON SCRIPT] Script URI:
   {py_script.absolute().as_uri()}""")
        print("Script to be executed asyncronously: ", py_script.absolute().as_uri())
        shell_script = f"""
{f"cd {wdir}" if wdir is not None else ""}
{"ipython" if ipython else "python"} {"-i" if interactive else ""} {py_script}
"""
        shell_path = PathExtended.tmpfile(name="tmp_shell_script", suffix=".sh" if self.machine == "Linux" else ".ps1", folder="tmp_scripts/shell")
        shell_path.write_text(shell_script)
        if shell is None and self.machine == "Windows":
            shell = "pwsh"
        window = "start" if new_window and self.machine == "Windows" else ""
        os.system(f"{window} {terminal} {shell} {shell_script}")

    @staticmethod
    def is_user_admin() -> bool:  # adopted from: https://stackoverflow.com/questions/19672352/how-to-run-script-with-elevated-privilege-on-windows"""
        if os.name == "nt":
            try:
                return __import__("ctypes").windll.shell32.IsUserAnAdmin()
            except Exception:
                import traceback

                traceback.print_exc()
                print("Admin check failed, assuming not an admin.")
                return False
        else:
            return os.getuid() == 0  # Check for root on Posix

    #     @staticmethod
    #     def run_as_admin(file: PLike, params: Any, wait: bool = False):
    #         proce_info = install_n_import(library="win32com", package="pywin32", fromlist=["shell.shell.ShellExecuteEx"]).shell.shell.ShellExecuteEx(lpVerb='runas', lpFile=file, lpParameters=params)
    #         # TODO update PATH for this to take effect immediately.
    #         if wait: time.sleep(1)
    #         return proce_info

    @staticmethod
    def get_header(wdir: OPLike, toolbox: bool):
        return f"""
# >> Code prepended
{"from crocodile.toolbox import *" if toolbox else "# No toolbox import."}
{'''sys.path.insert(0, r'{wdir}') ''' if wdir is not None else "# No path insertion."}
# >> End of header, start of script passed
"""
