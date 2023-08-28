
"""Devops Devapps Install
"""

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options
from typing import Any, Optional


if system() == "Windows": from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
elif system() == "Linux": from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
else: raise NotImplementedError(f"System {system()} not supported")


def main(program_name: Optional[str] = None):
    installers = get_cli_py_installers()
    default = tb.P("all")
    installers.list.insert(0, default)
    installers.list.insert(0, tb.P("System Installers"))
    installers.list.insert(0, tb.P("Other dev apps"))
    options = list(installers.apply(lambda x: x.stem + ((' -- ' + str(x.readit().__doc__)) if x.exists() else '')))
    # options.sort()  # throws off sync between installers and options

    if program_name is None:
        program_names = display_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default), fzf=True, multi=True)
        total_program = ""
        for program_name in program_names:
            assert isinstance(program_name, str), f"program_name is not a string: {program_name}"
            total_program += "\n" + get_program(program_name=program_name, options=options, installers=list(installers))
    else:
        total_program = get_program(program_name=program_name, options=options, installers=list(installers))
    return total_program


def get_program(program_name: str, options: list[Any], installers: list[tb.P]):
    if program_name == "all":
        if system() == "Linux":
            from machineconfig.jobs.python.python_linux_installers_all import main as main2
        elif system() == "Windows":
            from machineconfig.jobs.python.python_windows_installers_all import main as main2
        else: raise NotImplementedError(f"System {system()} not supported")
        main2()
        # program_linux = f"source {LIBRARY_ROOT}/setup_linux/devapps.sh"
        # program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
        program = ""
    elif program_name == "System Installers":
        if system() == "Windows": options_more = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
        elif system() == "Linux": options_more = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
        else: raise NotImplementedError(f"System {system()} not supported")
        program_names = display_options(msg="", options=sorted(list(options_more.keys())), header="CHOOSE DEV APP", fzf=True, multi=True)
        program = ""
        for name in program_names:
            sub_program = options_more[name]
            if sub_program.startswith("#winget"): sub_program = sub_program[1:]
            program += "\n" + sub_program
    elif program_name == "Other dev apps":
        installers = get_cli_py_installers(dev=True).list
        options = tb.L(installers).apply(lambda x: x.stem + ((' -- ' + str(x.readit().__doc__)) if x.exists() else '')).list
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
    else:
        idx = options.index(program_name)
        print(installers[idx])
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
    return program


def parse_apps_installer_linux(txt: str):
    txts = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    return tb.Struct.from_keys_values_pairs(tb.L(txts).apply(lambda tmp: (tmp.split('----')[0].rstrip().lstrip(), "\n".join(tmp.split("\n")[1:])))[1:])


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
