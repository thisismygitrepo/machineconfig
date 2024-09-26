
"""Devops Devapps Install
"""

# import subprocess
from tqdm import tqdm
from crocodile.core import List as L
from machineconfig.utils.utils import LIBRARY_ROOT, choose_multiple_options
from machineconfig.utils.installer import get_installers, install_all, Installer, get_all_dicts
from platform import system
from typing import Any, Optional, Literal, TypeAlias, get_args


WHICH_CAT: TypeAlias = Literal["AllEssentials", "EssentialsAndOthers", "SystemInstallers", "OtherDevApps", "PrecheckedCloudInstaller"]


def main(which: Optional[str] = None):
    if which is not None and which in get_args(WHICH_CAT):
        return get_programs_by_category(program_name=which)

    if which is not None:
        kv = {}
        for k, v in get_all_dicts(system=system()).items():
            kv.update(v)
        if which not in kv:
            raise ValueError(f"{which=} not found in {kv.keys()}")
        print(f"Installing {which}", kv[which])
        installer = Installer.from_dict(name=which, d=kv[which])
        print(installer)
        program = installer.install_robust(version=None)  # finish the task
        program = "echo 'Finished Installation'"  # write an empty program
        return program

    sys = system()
    installers = get_installers(dev=False, system=sys)  # + get_installers(dev=True, system=sys)
    default = "AllEssentials"
    options = ["SystemInstallers", "OtherDevApps", "EssentialsAndOthers", "PrecheckedCloudInstaller", default]
    options = [x.get_description() for x in tqdm(installers, desc="Checking installed programs")] + options

    program_names = choose_multiple_options(msg="", options=options, header="CHOOSE DEV APP", default=str(default))
    total_program = ""
    for which in program_names:
        assert isinstance(which, str), f"program_name is not a string: {which}"
        total_program += "\n" + get_programs_by_category(program_name=which, options=options, installers=list(installers))
    return total_program


def get_programs_by_category(program_name: WHICH_CAT):
    match program_name:
        case "AllEssentials" | "EssentialsAndOthers":
            installers_ = get_installers(dev=False, system=system())
            if program_name == "EssentialsAndOthers":
                installers_ += get_installers(dev=True, system=system())
            install_all(installers=L(installers_))
            program = ""
        case "SystemInstallers":
            if system() == "Windows": options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text())
            elif system() == "Linux":
                options_system_1 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps_dev.sh").read_text())
                options_system_2 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text())
                options_system = {**options_system_1, **options_system_2}
            else: raise NotImplementedError(f"System {system()} not supported")
            program_names = choose_multiple_options(msg="", options=sorted(list(options_system.keys())), header="CHOOSE DEV APP")
            program = ""
            for name in program_names:
                sub_program = options_system[name]
                if sub_program.startswith("#winget"): sub_program = sub_program[1:]
                program += "\n" + sub_program
        case "OtherDevApps":
            installers = get_installers(dev=True, system=system())
            options__: list[str] = [x.get_description() for x in tqdm(installers, desc="Checking installed programs")]
            program_names = choose_multiple_options(msg="", options=sorted(options__) + ["all"], header="CHOOSE DEV APP")
            if "all" in program_names: program_names = options__
            program = ""
            print("Installing:")
            L(program_names).print()
            for name in program_names:
                try:
                    idx = options__.index(name)
                except ValueError as ve:
                    print(f"{name=}")
                    print(f"{options__=}")
                    raise ve
                print(f"Installing {name}")
                sub_program = installers[idx].install_robust(version=None)  # finish the task
        case  "PrecheckedCloudInstaller":
            from machineconfig.jobs.python.check_installations import PrecheckedCloudInstaller
            ci = PrecheckedCloudInstaller()
            ci.download_safe_apps(name="AllEssentials")
            program = ""
    return program


def parse_apps_installer_linux(txt: str) -> dict[str, Any]:
    txts = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    res = {}
    for chunk in txts[1:]:
        try:
            k = chunk.split('----')[0].rstrip().lstrip()
            v = "\n".join(chunk.split("\n")[1:])
            res[k] = v
        except IndexError as e:
            print(chunk)
            raise e
    return res


def parse_apps_installer_windows(txt: str) -> dict[str, Any]:
    chunks: list[str] = []
    for idx, item in enumerate(txt.split(sep="winget install")):
        if idx == 0: continue
        if idx == 1: chunks.append(item)
        else: chunks.append("winget install" + item)
    # progs = L(txt.splitlines()).filter(lambda x: x.startswith("winget ") or x.startswith("#winget"))
    res: dict[str, str] = {}
    for a_chunk in chunks:
        try:
            name = a_chunk.split('--name ')[1]
            if "--Id" not in name:
                print(f"Warning: {name} does not have an Id, skipping")
                continue
            name = name.split(' --Id ', maxsplit=1)[0].strip('"').strip('"')
            res[name] = a_chunk
        except IndexError as e:
            print(a_chunk)
            raise e
    # Struct(res).print(as_config=True)
    # L(chunks).print(sep="-----------------------------------------------------------------------\n\n")
    # import time
    # time.sleep(10)
    return res


if __name__ == '__main__':
    pass
