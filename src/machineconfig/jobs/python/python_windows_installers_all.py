
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
import machineconfig.jobs.python_generic_installers as gens


def get_installers():
    return tb.P(inst.__file__).parent.search("*.py") + tb.P(gens.__file__).parent.search("*.py")


def main():
    get_installers().apply(tb.Read.py)


if __name__ == '__main__':
    main()
