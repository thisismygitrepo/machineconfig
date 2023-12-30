
"""Devops Devapps Install
"""

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, choose_multiple_options
from machineconfig.utils.installer import get_cli_py_installers_v2, Installer, install_all_v2
from typing import Any, Optional, Literal, TypeAlias


WHICH: TypeAlias = Literal["AllEssentials", "EssentialsAndOthers", "SystemInstallers", "OtherDevApps", "PrecheckedCloudInstaller"]


def main(which: Optional[str] = None):
    sys = system()
    installers = get_cli_py_installers_v2(dev=False, system=sys)
    default = "AllEssentials"
    options = ["SystemInstallers", "OtherDevApps", "EssentialsAndOthers", "PrecheckedCloudInstaller"]
    options = [default] + options
    options = [x.get_description() for x in installers] + options

    if which is not None:
        return get_program(program_name=which, options=options, installers=list(installers))

    program_names = choose_multiple_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default))
    total_program = ""
    for which in program_names:
        assert isinstance(which, str), f"program_name is not a string: {which}"
        total_program += "\n" + get_program(program_name=which, options=options, installers=list(installers))
    return total_program


def get_program(program_name: str, options: list[str], installers: list[Installer]):
    if program_name == "AllEssentials" or program_name == "EssentialsAndOthers":
        installers_ = get_cli_py_installers_v2(dev=False, system=system())
        if program_name == "EssentialsAndOthers":
            installers_ += get_cli_py_installers_v2(dev=True, system=system())
        install_all_v2(installers=tb.L(installers))
        program = ""
    elif program_name == "SystemInstallers":
        if system() == "Windows": options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
        elif system() == "Linux": options_system = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
        else: raise NotImplementedError(f"System {system()} not supported")
        program_names = choose_multiple_options(msg="", options=sorted(list(options_system.keys())), header="CHOOSE DEV APP")
        program = ""
        for name in program_names:
            sub_program = options_system[name]
            if sub_program.startswith("#winget"): sub_program = sub_program[1:]
            program += "\n" + sub_program
    elif program_name == "OtherDevApps":
        installers = get_cli_py_installers_v2(dev=True, system=system())
        options__: list[str] = [x.get_description() for x in installers]
        program_names = choose_multiple_options(msg="", options=sorted(options__), header="CHOOSE DEV APP")
        program = ""
        for name in program_names:
            try:
                idx = options__.index(name)
            except ValueError as ve:
                print(f"{name=}")
                print(f"{options__=}")
                raise ve
            sub_program = installers[idx].install_robust(version=None)  # finish the task
            # sub_program = "echo 'Finished Installation'"  # write an empty program
            # program += "\n" + ""sub_program
    elif program_name == "PrecheckedCloudInstaller":
        from machineconfig.jobs.python.check_installations import PrecheckedCloudInstaller
        ci = PrecheckedCloudInstaller()
        ci.download_safe_apps(name="AllEssentials")
        program = ""
    else:
        idx = options.index(program_name)
        print(installers[idx])
        program = installers[idx].install_robust(version=None)  # finish the task
        program = "echo 'Finished Installation'"  # write an empty program
    return program


def parse_apps_installer_linux(txt: str) -> dict[str, Any]:
    txts = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    res = {}
    for chunk in txts[1:]:
        try:
            k = chunk.split('----')[0].rstrip().lstrip()
            v = "\n".join(chunk.split("\n")[1:])
            res[k] = v
        except IndexError as e:
            print(chunk)
            raise e
    return res


def parse_apps_installer_windows(txt: str) -> dict[str, Any]:
    chunks: list[str] = []
    for idx, item in enumerate(txt.split(sep="winget install")):
        if idx == 0: continue
        if idx == 1: chunks.append(item)
        else: chunks.append("winget install" + item)
    # progs = tb.L(txt.splitlines()).filter(lambda x: x.startswith("winget ") or x.startswith("#winget"))
    res: dict[str, str] = {}
    for a_chunk in chunks:
        try:
            name = a_chunk.split('--name ')[1]
            if "--Id" not in name:
                print(f"Warning: {name} does not have an Id, skipping")
                continue
            name = name.split(' --Id ', maxsplit=1)[0].strip('"').strip('"')
            res[name] = a_chunk
        except IndexError as e:
            print(a_chunk)
            raise e
    # tb.Struct(res).print(as_config=True)
    # tb.L(chunks).print(sep="-----------------------------------------------------------------------\n\n")
    # import time
    # time.sleep(10)
    return res


if __name__ == '__main__':
    pass
