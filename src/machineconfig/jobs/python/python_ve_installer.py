

import crocodile.toolbox as tb
import platform
import machineconfig

system = platform.system()
lib_root = tb.P(machineconfig.__file__).parent


def ve_setup():
    dotted_py_version = input("Enter python version (e.g. 3.11): ")
    env_name = input("Enter virtual environment name: ")
    repos = input("Install essential repos? ([y]/n): ") or "y"

    env_path = tb.P.home().joinpath(env_name)
    if env_path.exists(): env_path.delete(sure=True)

    scripts = lib_root.joinpath(f"setup_{system.lower()}/ve.{'ps1' if system == 'Windows' else 'sh'}").read_text()
    scripts = tb.modify_text(raw=scripts, txt="ve_name=", alt=f"$ve_name='{env_name}'", newline=True)
    scripts = tb.modify_text(raw=scripts, txt="py_version=", alt=f"$py_version='{dotted_py_version.replace('.', '') if system == 'Windows' else dotted_py_version}'", newline=True)

    if repos:
        text = lib_root.joinpath(f"setup_{system.lower()}/repos.{'ps1' if system == 'Windows' else 'sh'}").read_text()
        text = tb.modify_text(raw=text, txt="ve_name=", alt=f"$ve_name='{env_name}'", newline=True)
        scripts += text

    print("Scrupt to create virtual environment...".center(50, "-"))
    print(scripts)
    print("".center(50, "-"))
    
    return scripts


if __name__ == '__main__':
    pass
