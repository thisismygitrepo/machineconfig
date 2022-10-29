
import crocodile.toolbox as tb
import machineconfig.jobs.python_windows_installers as inst
import machineconfig.jobs.python_generic_installers as gens


def get_installers():
    return tb.P(inst.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + tb.P(gens.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def main():
    fail = []
    for py_file in get_installers():
        try:
            tb.Read.py(py_file)["main"]()
        except Exception as ex:
            print(ex)
            fail.append(py_file)
    print(f"Failed: {fail}")
    print("Completed Installation".center(100, "-"))


if __name__ == '__main__':
    main()
