

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def main(program_name=None):
    if system() == "Windows":
        from machineconfig.jobs.python.python_windows_installers_all import get_cli_py_installers
    else:
        from machineconfig.jobs.python.python_linux_installers_all import get_cli_py_installers
    installers = get_cli_py_installers()
    default = tb.P("all")
    installers.list.insert(0, default)
    installers.list.insert(0, tb.P("Other"))
    options = list(installers.stem)
    options.sort()

    if program_name is None:
        program_name = display_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default))

    if program_name == "all":
        # program_linux = f"source {LIBRARY_ROOT}/setup_linux/devapps.sh"
        # program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
        if system() == "Linux":
            from machineconfig.jobs.python.python_linux_installers_all import main
            main()
        elif system() == "Windows":
            from machineconfig.jobs.python.python_windows_installers_all import main
            main()
        else:
            raise NotImplementedError(f"System {system()} not supported")
        program = ""
    elif program_name == "Other":
        if system() == "Windows":
            options_more = parse_apps_installer(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
        elif system() == "Linux":
            options_more = parse_apps_installer(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
        program = ""

    else:
        idx = installers.stem.list.index(program_name)
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
    return program


def parse_apps_installer(txt):
    txt = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    return tb.Struct.from_keys_values_pairs(tb.L(txt).apply(lambda tmp:  (tmp.split('----')[0].rstrip().lstrip(), "\n".join(tmp.split("\n")[1:])))[1:])


if __name__ == '__main__':
    pass
