from pathlib import Path
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
import platform
import subprocess
from typing import Optional, Union, Iterable
from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH, LINUX_INSTALL_PATH


def check_tool_exists(tool_name: str) -> bool:
    if platform.system() == "Windows":
        tool_name = tool_name.replace(".exe", "") + ".exe"
        res1 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name).is_file()])
        tool_name = tool_name.replace(".exe", "") + ".exe"
        res2 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name).is_file()])
        return res1 or res2
    elif platform.system() in ["Linux", "Darwin"]:
        root_path = Path(LINUX_INSTALL_PATH)
        return any([Path("/usr/local/bin").joinpath(tool_name).is_file(), Path("/usr/bin").joinpath(tool_name).is_file(), root_path.joinpath(tool_name).is_file()])
    else:
        raise NotImplementedError(f"platform {platform.system()} not implemented")
    # _ = cmd
    #     cmd = "where.exe"
    #     cmd = "which"
    # try:  # talking to terminal is too slow.
    #     _tmp = subprocess.check_output([cmd, tool_name], stderr=subprocess.DEVNULL)
    #     res: bool = True
    # except (subprocess.CalledProcessError, FileNotFoundError):
    #     res = False
    # return res
    # return root_path.joinpath(tool_name).is_file()


def choose_one_option[T](options: Iterable[T], header: str = "", tail: str = "", prompt: str = "", msg: str = "", default: Optional[T] = None, fzf: bool = False, custom_input: bool = False) -> T:
    choice_key = display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=False, custom_input=custom_input)
    assert not isinstance(choice_key, list)
    return choice_key


def choose_multiple_options[T](options: Iterable[T], header: str = "", tail: str = "", prompt: str = "", msg: str = "", default: Optional[T] = None, custom_input: bool = False) -> list[T]:
    choice_key = display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=True, multi=True, custom_input=custom_input)
    if isinstance(choice_key, list):
        return choice_key
    return [choice_key]


def display_options[T](msg: str, options: Iterable[T], header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, fzf: bool = False, multi: bool = False, custom_input: bool = False) -> Union[T, list[T]]:
    # TODO: replace with https://github.com/tmbo/questionary
    # # also see https://github.com/charmbracelet/gum
    tool_name = "fzf"
    options_strings: list[str] = [str(x) for x in options]
    default_string = str(default) if default is not None else None
    console = Console()
    if fzf and check_tool_exists(tool_name):
        from pyfzf.pyfzf import FzfPrompt

        fzf_prompt = FzfPrompt()
        nl = "\n"
        choice_string_multi: list[str] = fzf_prompt.prompt(choices=options_strings, fzf_options=("--multi" if multi else "") + f' --prompt "{prompt.replace(nl, " ")}" ')  # --border-label={msg.replace(nl, ' ')}")
        # --border=rounded doens't work on older versions of fzf installed at Ubuntu 20.04
        if not multi:
            try:
                choice_one_string = choice_string_multi[0]
                choice_idx = options_strings.index(choice_one_string)
                return list(options)[choice_idx]
            except IndexError as ie:
                print(f"❌ Error: {options=}, {choice_string_multi=}")
                print(f"🔍 Available choices: {choice_string_multi}")
                raise ie
        choice_idx_s = [options_strings.index(x) for x in choice_string_multi]
        return [list(options)[x] for x in choice_idx_s]
    else:
        if default is not None:
            assert default in options, f"Default `{default}` option not in options `{list(options)}`"
            default_msg = Text(" <<<<-------- DEFAULT", style="bold red")
        else:
            default_msg = Text("")
        txt = Text("\n" + msg + "\n")
        for idx, key in enumerate(options):
            txt = txt + Text(f"{idx:2d} ", style="bold blue") + str(key) + (default_msg if default is not None and default == key else "") + "\n"
        txt_panel = Panel(txt, title=header, subtitle=tail, border_style="bold red")

        console.print(txt_panel)
        if default is not None:
            choice_string = input(f"{prompt}\nEnter option number or hit enter for default choice: ")
        else:
            choice_string = input(f"{prompt}\nEnter option number: ")

        if choice_string == "":
            if default_string is None:
                console.print(Panel("🧨 Default option not available!", title="Error", expand=False))
                return display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
            choice_idx = options_strings.index(default_string)
            assert default is not None, "🧨 Default option not available!"
            choice_one: T = default
        else:
            try:
                choice_idx = int(choice_string, base=10)
                choice_one = list(options)[choice_idx]
            except IndexError as ie:  # i.e. converting to integer was successful but indexing failed.
                if choice_string in options_strings:  # string input
                    choice_idx = options_strings.index(choice_one)  # type: ignore
                    choice_one = list(options)[choice_idx]
                elif custom_input:
                    return str(choice_string)  # type: ignore
                else:
                    _ = ie
                    # raise ValueError(f"Unknown choice. {choice_string}") from ie
                    console.print(Panel(f"❓ Unknown choice: '{choice_string}'", title="Error", expand=False))
                    return display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
            except TypeError as te:  # int(choice_string) failed due to # either the number is invalid, or the input is custom.
                if choice_string in options_strings:  # string input
                    choice_idx = options_strings.index(choice_one)  # type: ignore
                    choice_one = list(options)[choice_idx]
                elif custom_input:
                    return choice_string  # type: ignore
                else:
                    _ = te
                    # raise ValueError(f"Unknown choice. {choice_string}") from te
                    console.print(Panel(f"❓ Unknown choice: '{choice_string}'", title="Error", expand=False))
                    return display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
        console.print(Panel(f"✅ Selected option {choice_idx}: {choice_one}", title="Selected", expand=False))
        if multi:
            return [choice_one]
    return choice_one


def choose_cloud_interactively() -> str:
    console = Console()
    console.print(Panel("🔍 LISTING CLOUD REMOTES | Fetching available cloud remotes...", border_style="bold blue", expand=False))
    result = subprocess.run("rclone listremotes", shell=True, capture_output=True, text=True)
    tmp = result.stdout if result.returncode == 0 else None
    if isinstance(tmp, str):
        remotes: list[str] = [x.replace(":", "") for x in tmp.splitlines()]

    else:
        raise ValueError(f"Got {tmp} from rclone listremotes")
    if len(remotes) == 0:
        raise RuntimeError("You don't have remotes. Configure your rclone first to get cloud services access.")
    cloud: str = choose_one_option(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0], fzf=True)
    console.print(Panel(f"✅ SELECTED CLOUD | {cloud}", border_style="bold blue", expand=False))
    return cloud


def get_ssh_hosts() -> list[str]:
    from paramiko import SSHConfig

    c = SSHConfig()
    c.parse(open(Path.home().joinpath(".ssh/config"), encoding="utf-8"))
    return list(c.get_hostnames())


def choose_ssh_host(multi: bool = True):
    return display_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
