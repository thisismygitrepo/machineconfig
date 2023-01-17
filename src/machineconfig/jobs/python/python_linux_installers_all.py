
import crocodile.toolbox as tb
import machineconfig.jobs.python_linux_installers as inst
import machineconfig.jobs.python_generic_installers as gens


def get_installers():
    return tb.P(inst.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + tb.P(gens.__file__).parent.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def main():
    installers = tb.L(get_installers())

    def install_logic(py_file):
        try:
            old_version = tb.Terminal().run(f"{py_file.stem} --version", shell="powershell").op[:-1]
            tb.Read.py(py_file)["main"]()
            new_version = tb.Terminal().run(f"{py_file.stem} --version", shell="powershell").op[:-1]
            if old_version == new_version:
                return f"😑 {py_file.stem} ==> same version: {old_version}"
            else:
                return f"🤩 {py_file.stem} ====> updated from {old_version} to {new_version}"
        except Exception as ex:
            print(ex)
            return f"Failed at {py_file.stem} with {ex}"

    install_logic(installers[0])  # try out the first installer alone cause it will ask for password, so the rest will inherit the sudo session.
    res = installers[1:].apply(install_logic, jobs=10)

    from rich.console import Console
    console = Console()

    print("\n")
    console.rule("Same version apps")
    print(f"{res.filter(lambda x: 'same version' in x).print()}")
    print("\n")
    console.rule("Updated apps")
    print(f"{res.filter(lambda x: 'updated from' in x).print()}")
    print("\n")
    print(f"{res.filter(lambda x: 'Failed at' in x).print()}")
    print("\n")
    console.rule("Failed apps")
    print("Completed Installation".center(100, "-"))
    print("\n" * 2)


if __name__ == '__main__':
    main()
