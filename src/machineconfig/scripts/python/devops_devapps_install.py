
"""Devops Devapps Install
"""

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options
from machineconfig.utils.installer import get_cli_py_installers
from typing import Any, Optional, Literal, TypeAlias


WHICH: TypeAlias = Literal["AllEssentials", "EssentialsAndOthers", "SystemInstallers", "OtherDevApps", "PrecheckedCloudInstaller"]


def main(which: Optional[str] = None):

    installers = get_cli_py_installers(dev=False)
    default = tb.P("AllEssentials")
    installers.list.insert(0, default)
    installers.list.insert(0, tb.P("SystemInstallers"))
    installers.list.insert(0, tb.P("OtherDevApps"))
    installers.list.insert(0, tb.P("EssentialsAndOthers"))
    installers.list.insert(0, tb.P("PrecheckedCloudInstaller"))
    options: list[str] = installers.apply(lambda x: x.stem + (' -- ' + x.readit()['__doc__'].lstrip().rstrip()) if x.exists() else x.stem).to_list()

    if which is not None:
        return get_program(program_name=which, options=options, installers=list(installers))

    program_names = display_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default), fzf=True, multi=True)
    total_program = ""
    for which in program_names:
        assert isinstance(which, str), f"program_name is not a string: {which}"
        total_program += "\n" + get_program(program_name=which, options=options, installers=list(installers))
    return total_program


def get_program(program_name: str, options: list[Any], installers: list[tb.P]):
    if program_name == "AllEssentials" or program_name == "EssentialsAndOthers":
        from machineconfig.utils.installer import install_all
        install_all(dev=False)
        if program_name == "EssentialsAndOthers": install_all(dev=True)
        program = ""
    elif program_name == "SystemInstallers":
        if system() == "Windows": options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
        elif system() == "Linux": options_system = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
        else: raise NotImplementedError(f"System {system()} not supported")
        program_names = display_options(msg="", options=sorted(list(options_system.keys())), header="CHOOSE DEV APP", fzf=True, multi=True)
        program = ""
        for name in program_names:
            sub_program = options_system[name]
            if sub_program.startswith("#winget"): sub_program = sub_program[1:]
            program += "\n" + sub_program
    elif program_name == "OtherDevApps":
        installers = get_cli_py_installers(dev=True).list
        options = tb.L(installers).apply(lambda x: x.stem + ((' -- ' + str(x.readit()['__doc__']).rstrip()) if x.exists() else '')).list
        program_names = display_options(msg="", options=sorted(options), header="CHOOSE DEV APP", fzf=True, multi=True)
        program = ""
        for name in program_names:
            idx = options.index(name)
            try:
                sub_program = installers[idx].readit()['main']()  # finish the task
            except KeyError as ke:
                print(f"KeyError: could not find 'main' in {installers[idx]}")
                raise KeyError from ke
            if sub_program is None: sub_program = "echo 'Finished Installation'"  # write an empty program
            program += "\n" + sub_program
    elif program_name == "PrecheckedCloudInstaller":
        from machineconfig.jobs.python.check_installations import PrecheckedCloudInstaller
        ci = PrecheckedCloudInstaller()
        ci.download_safe_apps(name="AllEssentials")
        program = ""
    else:
        idx = options.index(program_name)
        print(installers[idx])
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
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
    progs = tb.L(txt.splitlines()).filter(lambda x: x.startswith("winget ") or x.startswith("#winget"))
    res = {}
    for line in progs:
        try: res[line.split('--name ')[1].split(' --Id ')[0].strip('"').strip('"')] = line
        except IndexError as e:
            print(line)
            raise e
    return res


if __name__ == '__main__':
    pass
