
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
import machineconfig.jobs.python_generic_installers as gens
from machineconfig.jobs.python.python_linux_installers_all import main as linux_main


def get_cli_py_installers():
    return tb.P(inst.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + tb.P(gens.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def main():
    installers = tb.L(get_cli_py_installers())
    linux_main(installers=installers)


if __name__ == '__main__':
    main()
