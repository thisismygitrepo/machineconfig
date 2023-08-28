
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
import machineconfig.jobs.python_generic_installers as gens
from machineconfig.jobs.python.python_linux_installers_all import main as linux_main


def get_cli_py_installers(dev: bool = False):
    path = tb.P(inst.__file__).parent
    gens_path = tb.P(gens.__file__).parent
    if dev:
        path = path.joinpath("dev")
        gens_path = gens_path.joinpath("dev")
    return path.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + gens_path.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def main(dev: bool = False):
    installers = tb.L(get_cli_py_installers(dev=dev))
    linux_main(installers=installers)


if __name__ == '__main__':
    main(dev=False)
