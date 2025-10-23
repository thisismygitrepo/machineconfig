from pathlib import Path
from machineconfig.utils.installer_utils.installer_abc import check_tool_exists
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
import subprocess
from typing import Optional, Union, Iterable, overload, Literal, cast


# def strip_ansi_codes(text: str) -> str:
#     """Remove ANSI color codes from text."""
#     import re
#     return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


@overload
def choose_from_options[T](msg: str, options: Iterable[T], multi: Literal[False], custom_input: bool = False, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, fzf: bool = False) -> T: ...
@overload
def choose_from_options[T](msg: str, options: Iterable[T], multi: Literal[True], custom_input: bool = True, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, fzf: bool = False, ) -> list[T]: ...
def choose_from_options[T](msg: str, options: Iterable[T], multi: bool, custom_input: bool = True, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, fzf: bool = False, ) -> Union[T, list[T]]:
    # TODO: replace with https://github.com/tmbo/questionary
    # # also see https://github.com/charmbracelet/gum
    options_strings: list[str] = [str(x) for x in options]
    default_string = str(default) if default is not None else None
    console = Console()
    fzf_exists = check_tool_exists("fzf")
    # print("\n" * 10, f"{fzf=}, {fzf_exists=}", "\n" * 10)
    if fzf and fzf_exists:
        from pyfzf.pyfzf import FzfPrompt
        fzf_prompt = FzfPrompt()
        nl = "\n"
        choice_string_multi: list[str] = fzf_prompt.prompt(choices=options_strings, fzf_options=("--multi" if multi else "") + f' --prompt "{prompt.replace(nl, " ")}" --ansi')  # --border-label={msg.replace(nl, ' ')}")
        # --border=rounded doens't work on older versions of fzf installed at Ubuntu 20.04
        if not multi:
            try:
                choice_one_string = choice_string_multi[0]
                if isinstance(list(options)[0], str): return cast(T, choice_one_string)
                choice_idx = options_strings.index(choice_one_string)
                return list(options)[choice_idx]
            except IndexError as ie:
                print(f"❌ Error: {options=}, {choice_string_multi=}")
                print(f"🔍 Available choices: {choice_string_multi}")
                raise ie
        if isinstance(list(options)[0], str):
            return cast(list[T], choice_string_multi)
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
            choice_string = input(f"{prompt}\nEnter option number/name or hit enter for default choice: ")
        else:
            choice_string = input(f"{prompt}\nEnter option number/name: ")

        if choice_string == "":
            if default_string is None:
                console.print(Panel("🧨 Default option not available!", title="Error", expand=False))
                return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
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
                    return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
            except (TypeError, ValueError) as te:  # int(choice_string) failed due to # either the number is invalid, or the input is custom.
                if choice_string in options_strings:  # string input
                    choice_idx = options_strings.index(choice_one)  # type: ignore
                    choice_one = list(options)[choice_idx]
                elif custom_input:
                    return choice_string  # type: ignore
                else:
                    _ = te
                    # raise ValueError(f"Unknown choice. {choice_string}") from te
                    console.print(Panel(f"❓ Unknown choice: '{choice_string}'", title="Error", expand=False))
                    return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
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
    cloud: str = choose_from_options(msg="WHICH CLOUD?", multi=False, options=list(remotes), default=remotes[0], fzf=True)
    console.print(Panel(f"✅ SELECTED CLOUD | {cloud}", border_style="bold blue", expand=False))
    return cloud


def get_ssh_hosts() -> list[str]:
    from paramiko import SSHConfig

    c = SSHConfig()
    c.parse(open(Path.home().joinpath(".ssh/config"), encoding="utf-8"))
    return list(c.get_hostnames())


@overload
def choose_ssh_host(multi: Literal[False]) -> str: ...
@overload
def choose_ssh_host(multi: Literal[True]) -> list[str]: ...
def choose_ssh_host(multi: bool):
    return choose_from_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
