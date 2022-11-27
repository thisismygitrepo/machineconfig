

import crocodile.toolbox as tb
import platform
import machineconfig

system = platform.system()
lib_root = tb.P(machineconfig.__file__).parent


def ve_setup():
    print("\n\n")
    print("Existing Python versions:\n=========================")
    tb.P.get_env().Path.search("python.exe").reduce()[1:].print()
    print(f"\nExisting virtual environments are:")
    ves = tb.P.home().joinpath("venvs").search("*", files=False).apply(lambda a_ve: (a_ve.name, a_ve.joinpath("pyvenv.cfg").read_text()))
    ves.apply(lambda a_ve: print(f"{a_ve[0]}\n{'-' * 10}\n{a_ve[1]}\n"))
    dotted_py_version = input("Enter python version (3.11): ") or "3.11"
    env_name = input("Enter virtual environment name (latest): ") or "latest"
    repos = input("Install essential repos? ([y]/n): ") or "y"

    env_path = tb.P.home().joinpath("venvs", env_name)
    if env_path.exists(): env_path.delete(sure=True)

    scripts = lib_root.joinpath(f"setup_{system.lower()}/ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    variable_prefix = "$" if system == "Windows" else ""
    scripts = tb.modify_text(raw=scripts, txt="ve_name=", alt=f"{variable_prefix}ve_name='{env_name}'", newline=True)
    scripts = tb.modify_text(raw=scripts, txt="py_version=", alt=f"{variable_prefix}py_version='{dotted_py_version.replace('.', '') if system == 'Windows' else dotted_py_version}'", newline=True)

    if repos == "y":
        text = lib_root.joinpath(f"setup_{system.lower()}/repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
        text = tb.modify_text(raw=text, txt="ve_name=", alt=f"{variable_prefix}ve_name='{env_name}'", newline=True)
        scripts += text

    print("Script to create virtual environment...".center(80, "-"))
    print(scripts)
    print("".center(80, "-"))

    return scripts


if __name__ == '__main__':
    pass
