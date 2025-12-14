
from pathlib import Path
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
import subprocess
from typing import Optional, Union, Iterable, overload, Literal, cast

@overload
def choose_from_options[T](options: Iterable[T], msg: str, multi: Literal[False], custom_input: bool = False, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, tv: bool = False, preview: Optional[Literal["bat"]]=None) -> T: ...
@overload
def choose_from_options[T](options: Iterable[T], msg: str, multi: Literal[True], custom_input: bool = True, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, tv: bool = False, preview: Optional[Literal["bat"]]=None) -> list[T]: ...
def choose_from_options[T](options: Iterable[T], msg: str, multi: bool, custom_input: bool = True, header: str = "", tail: str = "", prompt: str = "", default: Optional[T] = None, tv: bool = False, preview: Optional[Literal["bat"]]=None, ) -> Union[T, list[T]]:
    # TODO: replace with https://github.com/tmbo/questionary
    # # also see https://github.com/charmbracelet/gum
    options_strings: list[str] = [str(x) for x in options]
    default_string = str(default) if default is not None else None
    console = Console()
    from machineconfig.utils.installer_utils.installer_locator_utils import check_tool_exists
    # from machineconfig.utils.installer_utils.installer_cli import check_tool_exists
    # print("ch1")
    if tv and check_tool_exists("tv"):
        from machineconfig.utils.accessories import randstr
        options_txt_path = Path.home().joinpath("tmp_results/tmp_files/choices_" + randstr(6) + ".txt")
        options_txt_path.parent.mkdir(parents=True, exist_ok=True)
        options_txt_path.write_text("\n".join(options_strings), encoding="utf-8")

        # Run `tv` interactively so the user can make selections. We redirect tv's
        # stdout to a temporary output file so we can read the chosen lines after
        # the interactive session completes. Do not capture_output or redirect
        # stdin/stderr here so `tv` stays attached to the terminal.
        tv_out_path = options_txt_path.with_name(options_txt_path.stem + "_out.txt")
        if preview is None:
            preview_line = ""
        elif preview == "bat":
            preview_line = r"""--preview-command "bat -n --color=always {}" --preview-size 70 """
        
        import platform
        if platform.system() == "Windows":
            # PowerShell + TUI apps can be finicky when stdin is a pipe. Avoid piping into `tv` and
            # instead provide a `--source-command` so `tv` can keep stdin attached to the console.
            # Also: `tv --ansi` is a flag (no value). Passing `true` makes it a positional argument
            # (channel/path/command), which can lead to confusing behavior.
            source_cmd = f"cmd /C type \"{options_txt_path}\""
            tv_cmd = f"""
$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
tv  {preview_line} --ansi --source-command '{source_cmd}' --source-output "{{}}" | Out-File -Encoding utf8 -FilePath "{tv_out_path}" """
        else:
            source_cmd = f'cat "{options_txt_path}"'
            tv_cmd = f"""tv  {preview_line} --ansi --source-command "{source_cmd}" --source-output "{{}}" > "{tv_out_path}" """

        # print(f"Running tv command: {tv_cmd}")
        # print(f"Options file: {options_txt_path}")
        # print(f"Content:\n{options_txt_path.read_text(encoding='utf-8')}")
        # print(f"tv output file: {tv_out_path}")
        from machineconfig.utils.code import run_shell_script
        res = run_shell_script(tv_cmd, display_script=False, clean_env=False)
        
        # If tv returned a non-zero code and there is no output file, treat it as an error.
        if res.returncode != 0 and not tv_out_path.exists():
            raise RuntimeError(f"Got error running tv command: {tv_cmd}\nreturncode: {res.returncode}")

        # Read selections (if any) from the output file created by tv.
        print(f"Reading tv output from: {tv_out_path}")
        out_text = tv_out_path.read_text(encoding="utf-8-sig")
        choice_string_multi = [x for x in out_text.splitlines() if x.strip() != ""]

        # Cleanup temporary files
        options_txt_path.unlink(missing_ok=True)
        tv_out_path.unlink(missing_ok=True)
        if not multi:
            try:
                choice_one_string = choice_string_multi[0]
                if isinstance(list(options)[0], str):
                    print(f"✅ Selected option: {choice_one_string}")
                    return cast(T, choice_one_string)
                choice_idx = options_strings.index(choice_one_string)
                choice_made =  list(options)[choice_idx]
                print(f"✅ Selected option: {choice_made}")
                return choice_made
            except IndexError as ie:
                print(f"❌ Error: {options=}, {choice_string_multi=}")
                print(f"🔍 Available choices: {choice_string_multi}")
                raise ie
        if isinstance(list(options)[0], str):
            result2 = cast(list[T], choice_string_multi)
            print(f"✅ Selected options: {result2}")
            return result2
        choice_idx_s = [options_strings.index(x) for x in choice_string_multi]
        result = [list(options)[x] for x in choice_idx_s]
        print(f"✅ Selected options: {result}")
        return result
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
                return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, tv=tv, multi=multi, custom_input=custom_input)
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
                    return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, tv=tv, multi=multi, custom_input=custom_input)
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
                    return choose_from_options(msg=msg, options=options, header=header, tail=tail, prompt=prompt, default=default, tv=tv, multi=multi, custom_input=custom_input)
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
    cloud: str = choose_from_options(msg="WHICH CLOUD?", multi=False, options=list(remotes), default=remotes[0], tv=True)
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
    return choose_from_options(msg="", options=get_ssh_hosts(), multi=multi, tv=True)
