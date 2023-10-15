
"""
Utils
"""

from crocodile.file_management import P, randstr
from crocodile.meta import Terminal
from crocodile.core import install_n_import
# import crocodile.environment as env
import machineconfig
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.syntax import Syntax
import platform
from typing import Optional, Union, TypeVar


LIBRARY_ROOT = P(machineconfig.__file__).resolve().parent  # .replace(P.home().str.lower(), P.home().str)
REPO_ROOT = LIBRARY_ROOT.parent.parent
PROGRAM_PATH = (P.tmp().joinpath("shells/python_return_command") + (".ps1" if platform.system() == "Windows" else ".sh")).create(parents_only=True)
CONFIG_PATH = P.home().joinpath(".config/machineconfig")
DEFAULTS_PATH = P.home().joinpath("dotfiles/machineconfig/defaults.ini")
APP_VERSION_ROOT = P.home().joinpath(f"tmp_results/cli_tools_installers/versions")
TMP_INSTALL_DIR = P.tmp(folder="tmp_installers")


T = TypeVar("T")


def choose_cloud_interactively() -> str:
    from crocodile.core import List as L
    print(f"Listing Remotes ... ")
    tmp = Terminal().run("rclone listremotes").op_if_successfull_or_default(strict_returcode=False)
    # consider this: remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
    if isinstance(tmp, str):
        remotes = L(tmp.splitlines()).apply(lambda x: x.replace(":", ""))

    else: raise ValueError(f"Got {tmp} from rclone listremotes")
    if len(remotes) == 0:
        raise RuntimeError(f"You don't have remotes. Configure your rclone first to get cloud services access.")
    cloud = display_options(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0], fzf=True)
    assert isinstance(cloud, str)
    return cloud


def match_file_name(sub_string: str):
    """Look up current directory for file name that matches the passed substring."""
    search_results = P.cwd().absolute().search(f"*{sub_string}*.py", r=True)
    if len(search_results) == 1:
        path_obj = search_results.list[0]
    elif len(search_results) > 1:
        choice = display_options(msg=f"Search results are ambiguous or non-existent", options=search_results.list, fzf=True, multi=False)
        assert not isinstance(choice, list)
        path_obj = P(choice)
    else:
        msg = f"\n{'--' * 50}\n💥 Path {sub_string} does not exist. No search results\n{'--' * 50}\n"
        raise FileNotFoundError(msg)
    print(f"\n{'--' * 50}\n🔗 Mapped `{sub_string}` ➡️ `{path_obj}`\n{'--' * 50}\n")
    return path_obj


def display_options(msg: str, options: list[T], header: str = "", tail: str = "", prompt: str = "",
                    default: Optional[T] = None, fzf: bool = False, multi: bool = False, custom_input: bool = False) -> Union[T, list[T]]:
    tool_name = "fzf"
    if fzf and check_tool_exists(tool_name):
        install_n_import("pyfzf")
        from pyfzf.pyfzf import FzfPrompt
        fzf_prompt = FzfPrompt()
        nl = "\n"
        choice_key = fzf_prompt.prompt(choices=options, fzf_options=("--multi" if multi else "") + f' --prompt "{prompt.replace(nl, " ")}" --border=rounded')  # --border-label={msg.replace(nl, ' ')}")
        if not multi:
            try: choice_key = choice_key[0]
            except IndexError as ie:
                print(choice_key)
                raise ie
    else:
        console = Console()
        if default is not None:
            assert default in options, f"Default `{default}` option not in options `{list(options)}`"
            default_msg = Text(f" <<<<-------- DEFAULT", style="bold red")
        else: default_msg = Text("")
        txt = Text("\n" + msg + "\n")
        for idx, key in enumerate(options):
            txt = txt + Text(f"{idx:2d} ", style="bold blue") + str(key) + (default_msg if default is not None and default == key else "") + "\n"
        txt_panel = Panel(txt, title=header, subtitle=tail, border_style="bold red")
        console.print(txt_panel)
        choice_string = input(f"{prompt}\nEnter option *number* or hit enter for default choice: ")
        if choice_string == "":
            assert default is not None, f"Default option not available!"
            choice_idx = options.index(default)
            choice_key = default
        else:
            try:
                choice_idx = int(choice_string)
                choice_key = options[choice_idx]
            except IndexError as ie:  # i.e. converting to integer was successful but indexing failed.
                if choice_string in options:  # string input
                    choice_idx = options.index(choice_key)  # type: ignore #TODO: fix this
                    choice_key = options[choice_idx]
                elif custom_input: return str(choice_string)  # type: ignore #TODO: fix this
                else: raise ValueError(f"Unknown choice. {choice_string}") from ie
            except TypeError as te:  # int(choice_string) failed due to # either the number is invalid, or the input is custom.
                if choice_string in options:  # string input
                    choice_idx = options.index(choice_key)  # type: ignore #TODO: fix this
                    choice_key = options[choice_idx]
                elif custom_input: return str(choice_string)  # type: ignore #TODO: fix this
                else: raise ValueError(f"Unknown choice. {choice_string}") from te
        print(f"{choice_idx}: {choice_key}", f"<<<<-------- CHOICE MADE")
    return choice_key


def symlink(this: P, to_this: P, prioritize_to_this: bool = True):
    """helper function. creates a symlink from `this` to `to_this`.
    What can go wrong?
    depending on this and to_this existence, one will be prioretized depending on overwrite value.
    True means this will potentially be overwritten (depending on whether to_this exists or not)
    False means to_this will potentially be overwittten."""
    this = P(this).expanduser().absolute()
    to_this = P(to_this).expanduser().absolute()
    if this.is_symlink(): this.delete(sure=True)  # delete if it exists as symblic link, not a concrete path.
    if this.exists():  # this is a problem. It will be resolved via `overwrite`
        if prioritize_to_this is True:  # it *can* be deleted, but let's look at target first.
            if to_this.exists():  # this exists, to_this as well. to_this is prioritized.
                this.append(f".orig_{randstr()}", inplace=True)  # rename is better than deletion
            else: this.move(path=to_this)  # this exists, to_this doesn't. to_this is prioritized.
        elif prioritize_to_this is False:  # don't sacrefice this, sacrefice to_this.
            if to_this.exists(): this.move(path=to_this, overwrite=True)  # this exists, to_this as well, this is prioritized.   # now we are readly to make the link
            else: this.move(path=to_this)  # this exists, to_this doesn't, this is prioritized.
    else:  # this doesn't exist.
        if not to_this.exists(): to_this.touch()  # we have to touch it (file) or create it (folder)
    if platform.system() == "Windows": _ = install_n_import("win32api", "pywin32")  # this is crucial for windows to pop up the concent window in case python was not run as admin.
    try:
        P(this).symlink_to(to_this, verbose=True, overwrite=True)
    except Exception as ex: print(f"Failed at linking {this} ➡️ {to_this}.\nReason: {ex}")


def get_shell_script_executing_pyscript(python_file: str, func: Optional[str] = None, ve_name: str = "ve"):
    if func is None: exec_line = f"""python {python_file}"""
    else: exec_line = f"""python -m fire {python_file} {func}"""
    return f"""
. $HOME/scripts/activate_ve {ve_name}
{exec_line}
deactivate
"""


def write_shell_script(program: str, desc: str = "", preserve_cwd: bool = True, display: bool = True, execute: bool = False):
    if preserve_cwd:
        if platform.system() == "Windows":
            program = "$orig_path = $pwd\n" + program + "\ncd $orig_path"
        else:
            program = 'orig_path=$(cd -- "." && pwd)\n' + program + '\ncd "$orig_path" || exit'
    if display:
        print(f"Executing {PROGRAM_PATH}")
        print_programming_script(program=program, lexer="shell", desc=desc)
    if platform.system() == 'Windows': PROGRAM_PATH.create(parents_only=True).write_text(program)
    else: PROGRAM_PATH.create(parents_only=True).write_text(f"{program}")
    if execute: Terminal().run(f". {PROGRAM_PATH}", shell="powershell").print_if_unsuccessful(desc="Executing shell script", strict_err=True, strict_returncode=True)
    return None


def print_programming_script(program: str, lexer: str, desc: str = ""):
    if lexer == "shell":
        if platform.system() == "Windows": lexer = "powershell"
        elif platform.system() == "Linux": lexer = "sh"
        else: raise NotImplementedError(f"lexer {lexer} not implemented for system {platform.system()}")
    console = Console()
    console.print(Panel(Syntax(program, lexer=lexer), title=desc), style="bold red")


def get_latest_version(url: str) -> None:
    # not yet used, consider, using it.
    import requests
    import json
    url = f"https://api.github.com/repos/{url.split('github.com/')[1]}/releases/latest"
    # Replace {owner} and {repo} with the actual owner and repository name
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = json.loads(response.text)
        latest_version = data["tag_name"]
        print("Latest release version:", latest_version)
    else: print("Error:", response.status_code)


def check_tool_exists(tool_name: str) -> bool:
    if platform.system() == "Windows": tool_name = tool_name.replace(".exe", "") + ".exe"
    if platform.system() == "Windows": cmd = "where.exe"
    elif platform.system() == "Linux": cmd = "which"
    else: raise NotImplementedError(f"platform {platform.system()} not implemented")
    import subprocess
    try:
        subprocess.check_output([cmd, tool_name])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError): return False


def get_ssh_hosts() -> list[str]:
    from paramiko import SSHConfig
    c = SSHConfig()
    c.parse(open(P.home().joinpath(".ssh/config").str, encoding="utf-8"))
    return list(c.get_hostnames())
def choose_ssh_host(multi: bool = True): return display_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)


if __name__ == '__main__':
    # import typer
    # typer.run(check_tool_exists)
    pass
