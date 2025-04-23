from crocodile.core import List as L
from crocodile.meta import Terminal
from crocodile.file_management import P

# import crocodile.environment as env
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
import platform
import subprocess
from typing import Optional, Union, TypeVar, Iterable

T = TypeVar("T")



def check_tool_exists(tool_name: str, install_script: Optional[str] = None) -> bool:
    """This is the CLI equivalent of `install_n_import` function of crocodile. """
    if platform.system() == "Windows":
        tool_name = tool_name.replace(".exe", "") + ".exe"

    if platform.system() == "Windows": cmd = "where.exe"
    elif platform.system() == "Linux": cmd = "which"
    else: raise NotImplementedError(f"platform {platform.system()} not implemented")

    try:
        _tmp = subprocess.check_output([cmd, tool_name], stderr=subprocess.DEVNULL)
        res: bool=True
    except (subprocess.CalledProcessError, FileNotFoundError):
        res = False
    if res is False and install_script is not None:
        print(f"""
{'=' * 60}
📥 INSTALLING TOOL | Installing {tool_name}...
{'=' * 60}
""")
        Terminal().run(install_script, shell="powershell").print()
        return check_tool_exists(tool_name=tool_name, install_script=None)
    return res


def choose_one_option(options: Iterable[T], header: str="", tail: str="", prompt: str="", msg: str="",
                      default: Optional[T] = None, fzf: bool=False, custom_input: bool=False) -> T:
    choice_key = display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt,
                                 default=default, fzf=fzf, multi=False, custom_input=custom_input)
    assert not isinstance(choice_key, list)
    return choice_key


def choose_multiple_options(options: Iterable[T], header: str="", tail: str="", prompt: str="", msg: str="",
                            default: Optional[T] = None, custom_input: bool=False) -> list[T]:
    choice_key = display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt,
                                 default=default, fzf=True, multi=True,
                                 custom_input=custom_input)
    if isinstance(choice_key, list): return choice_key
    return [choice_key]


def display_options(msg: str, options: Iterable[T], header: str="", tail: str="", prompt: str="",
                    default: Optional[T] = None, fzf: bool=False, multi: bool=False, custom_input: bool=False) -> Union[T, list[T]]:
    # TODO: replace with https://github.com/tmbo/questionary
    # # also see https://github.com/charmbracelet/gum
    tool_name = "fzf"
    options_strings: list[str] = [str(x) for x in options]
    default_string = str(default) if default is not None else None
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
        console = Console()
        if default is not None:
            assert default in options, f"Default `{default}` option not in options `{list(options)}`"
            default_msg = Text(" <<<<-------- DEFAULT", style="bold red")
        else: default_msg = Text("")
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
                print("🧨 Default option not available!")
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
                elif custom_input: return str(choice_string)  # type: ignore
                else:
                    _ = ie
                    # raise ValueError(f"Unknown choice. {choice_string}") from ie
                    print(f"❓ Unknown choice: '{choice_string}'")
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
                    print(f"❓ Unknown choice: '{choice_string}'")
                    return display_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, fzf=fzf, multi=multi, custom_input=custom_input)
        print(f"✅ Selected option {choice_idx}: {choice_one}")
        if multi: return [choice_one]
    return choice_one


def choose_cloud_interactively() -> str:
    print(f"""
{'=' * 60}
🔍 LISTING CLOUD REMOTES | Fetching available cloud remotes...
{'=' * 60}
""")
    tmp = Terminal().run("rclone listremotes").op_if_successfull_or_default(strict_returcode=False)
    # consider this: remotes = Read.ini(P.home().joinpath(".config/rclone/rclone.conf")).sections()
    if isinstance(tmp, str):
        remotes: list[str] = L(tmp.splitlines()).apply(lambda x: x.replace(":", "")).list

    else: raise ValueError(f"Got {tmp} from rclone listremotes")
    if len(remotes) == 0:
        raise RuntimeError("You don't have remotes. Configure your rclone first to get cloud services access.")
    cloud: str = choose_one_option(msg="WHICH CLOUD?", options=list(remotes), default=remotes[0], fzf=True)
    print(f"""
✅ SELECTED CLOUD | {cloud}
{'=' * 60}
""")
    return cloud

def get_ssh_hosts() -> list[str]:
    from paramiko import SSHConfig
    c = SSHConfig()
    c.parse(open(P.home().joinpath(".ssh/config").to_str(), encoding="utf-8"))
    return list(c.get_hostnames())
def choose_ssh_host(multi: bool=True): return display_options(msg="", options=get_ssh_hosts(), multi=multi, fzf=True)
