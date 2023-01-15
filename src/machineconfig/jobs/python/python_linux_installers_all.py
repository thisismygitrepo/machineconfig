
import crocodile.toolbox as tb
import machineconfig.jobs.python_linux_installers as inst
import machineconfig.jobs.python_generic_installers as gens


def get_installers():
    return tb.P(inst.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + tb.P(gens.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def main():
    installers = tb.L(get_installers())

    def install_logic(py_file):
        try:
            tb.Read.py(py_file)["main"]()
            return None
        except Exception as ex:
            print(ex)
            return py_file

    install_logic(installers[0])  # try out the first installer alone cause it will ask for password, so the rest will inherit the sudo session.
    fail = installers[1:].apply(install_logic, jobs=10)
    fail = fail.filter(lambda x: x is not None)

    print("\n" * 2)
    print(f"Failed: {fail}")
    print("\n")
    print("Completed Installation".center(100, "-"))
    print("\n" * 2)


if __name__ == '__main__':
    main()
