

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def main(program_name=None):
    if system() == "Windows": from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
    elif system() == "Linux": from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
    else: raise NotImplementedError(f"System {system()} not supported")
    installers = get_cli_py_installers()
    default = tb.P("all")
    installers.list.insert(0, default)
    installers.list.insert(0, tb.P("System Installers"))
    installers.list.insert(0, tb.P("Other dev apps"))
    options = list(installers.apply(lambda x: x.stem + ((' -- ' + str(x.readit().__doc__)) if x.exists() else '')))
    options.sort()

    if program_name is None:
        program_name = display_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default), fzf=True)

    if program_name == "all":
        if system() == "Linux": from machineconfig.jobs.python.python_linux_installers_all import main
        elif system() == "Windows": from machineconfig.jobs.python.python_windows_installers_all import main
        else: raise NotImplementedError(f"System {system()} not supported")
        main()
        # program_linux = f"source {LIBRARY_ROOT}/setup_linux/devapps.sh"
        # program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
        program = ""
    elif program_name == "System Installers":
        if system() == "Windows": options_more = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
        elif system() == "Linux": options_more = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
        else: raise NotImplementedError(f"System {system()} not supported")
        program_name = display_options(msg="", options=list(options_more.keys()), header="CHOOSE DEV APP", fzf=True)
        program = options_more[program_name]
        if program.startswith("#"): program = program[1:]
        print(f"Running:\n{program}")
    elif program_name == "Other dev apps":
        installers = get_cli_py_installers(dev=True)
        options = list(installers.apply(lambda x: x.stem + ((' -- ' + str(x.readit().__doc__)) if x.exists() else '')))
        options.sort()
        program_name = display_options(msg="", options=options, header="CHOOSE DEV APP", fzf=True)
        idx = options.index(program_name)
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
    else:
        idx = options.index(program_name)
        print(installers[idx])
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
    return program


def parse_apps_installer_linux(txt):
    txt = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    return tb.Struct.from_keys_values_pairs(tb.L(txt).apply(lambda tmp:  (tmp.split('----')[0].rstrip().lstrip(), "\n".join(tmp.split("\n")[1:])))[1:])


def parse_apps_installer_windows(txt) -> dict:
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
