

from platform import system
# import subprocess
import crocodile.toolbox as tb
from machineconfig.utils.utils import LIBRARY_ROOT, display_options


def main(program_name=None):
    if system() == "Windows":
        from machineconfig.jobs.python.python_windows_installers_all import get_installers
    else:
        from machineconfig.jobs.python.python_linux_installers_all import get_installers
    installers = get_installers()
    default = tb.P("all")
    installers.list.insert(0, default)
    options = list(installers.stem)
    options.sort()

    if program_name is None:
        program_name = display_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default))

    if program_name == "all":
        program_linux = f"source {LIBRARY_ROOT}/setup_linux/devapps.sh"
        program_windows = f"{LIBRARY_ROOT}/setup_windows/devapps.ps1"
        program = program_linux if system() == "Linux" else program_windows
    else:
        idx = installers.stem.list.index(program_name)
        program = installers[idx].readit()['main']()  # finish the task
        if program is None: program = "echo 'Finished Installation'"  # write an empty program
    return program


if __name__ == '__main__':
    pass
