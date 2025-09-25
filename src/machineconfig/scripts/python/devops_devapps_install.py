"""Devops Devapps Install"""

# import subprocess
from machineconfig.utils.installer_utils.installer_class import Installer
from rich.progress import Progress, SpinnerColumn, TextColumn
from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.utils.options import choose_multiple_options
from machineconfig.utils.installer import get_installers, install_all, get_all_dicts
from platform import system
from typing import Any, Optional, Literal, TypeAlias, get_args


WHICH_CAT: TypeAlias = Literal["AllEssentials", "EssentialsAndOthers", "SystemInstallers", "PrecheckedCloudInstaller"]


def main(which: Optional[WHICH_CAT | str]) -> None:
    if which is not None and which in get_args(WHICH_CAT):  # install by category
        return get_programs_by_category(program_name=which)  # type: ignore

    if which is not None:  # install by name
        total_messages: list[str] = []
        for a_which in which.split(",") if type(which) == str else which:
            kv = {}
            for _category, v in get_all_dicts(system=system()).items():
                kv.update(v)
            if a_which not in kv:
                raise ValueError(f"{a_which=} not found in {kv.keys()}")
            print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🔧 Installing: {a_which}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            installer = Installer.from_dict(name=a_which, d=kv[a_which])
            print(installer)
            program = installer.install_robust(version=None)  # finish the task
            total_messages.append(program)
        for a_message in total_messages:
            print(a_message)
        return None

    # interactive installation
    installers = [Installer.from_dict(d=vd, name=name) for __kat, vds in get_all_dicts(system=system()).items() for name, vd in vds.items()]

    # Check installed programs with progress indicator
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("✅ Checking installed programs...", total=len(installers))
        options = []
        for x in installers:
            options.append(x.get_description())
            progress.update(task, advance=1)

    options += list(get_args(WHICH_CAT))
    # print("s"*1000)
    program_names = choose_multiple_options(msg="", options=options, header="🚀 CHOOSE DEV APP", default="AllEssentials")

    total_program = ""
    for _an_idx, a_program_name in enumerate(program_names):
        print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🔄 Processing: {a_program_name}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
        if a_program_name in get_args(WHICH_CAT):
            total_program += "\n" + get_programs_by_category(program_name=a_program_name)  # type: ignore
        else:
            an_installer = installers[options.index(a_program_name)]
            total_program += "\n" + an_installer.install_robust(version=None)  # finish the task
    import subprocess

    subprocess.run(total_program, shell=True, check=True)


def get_programs_by_category(program_name: WHICH_CAT):
    print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📦 Installing Category: {program_name}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    match program_name:
        case "AllEssentials" | "EssentialsAndOthers":
            installers_ = get_installers(dev=False, system=system())
            if program_name == "EssentialsAndOthers":
                installers_ += get_installers(dev=True, system=system())
            install_all(installers=installers_)
            program = ""

        case "SystemInstallers":
            if system() == "Windows":
                options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text(encoding="utf-8"))
            elif system() == "Linux":
                options_system_1 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps_dev.sh").read_text(encoding="utf-8"))
                options_system_2 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text(encoding="utf-8"))
                options_system = {**options_system_1, **options_system_2}
            else:
                raise NotImplementedError(f"❌ System {system()} not supported")
            program_names = choose_multiple_options(msg="", options=sorted(list(options_system.keys())), header="🚀 CHOOSE DEV APP")
            program = ""
            for name in program_names:
                print(f"""
┌────────────────────────────────────────────────────
│ ⚙️  Installing: {name}
└────────────────────────────────────────────────────""")
                sub_program = options_system[name]
                if sub_program.startswith("#winget"):
                    sub_program = sub_program[1:]
                program += "\n" + sub_program

        # case "OtherDevApps":
        #     installers = get_installers(dev=True, system=system())
        #     options__: list[str] = [x.get_description() for x in tqdm(installers, desc="Checking installed programs")]
        #     program_names = choose_multiple_options(msg="", options=sorted(options__) + ["all"], header="CHOOSE DEV APP")
        #     if "all" in program_names: program_names = options__
        #     program = ""
        #     print("Installing:")
        #     L(program_names).print()
        #     for name in program_names:
        #         try:
        #             idx = options__.index(name)
        #         except ValueError as ve:
        #             print(f"{name=}")
        #             print(f"{options__=}")
        #             raise ve
        #         print(f"Installing {name}")
        #         sub_program = installers[idx].install_robust(version=None)  # finish the task

        case "PrecheckedCloudInstaller":
            # from machineconfig.jobs.python.check_installations import PrecheckedCloudInstaller
            # ci = PrecheckedCloudInstaller()
            # ci.download_safe_apps(name="AllEssentials")
            # program = ""
            raise NotImplementedError("PrecheckedCloudInstaller is not implemented yet.")
    return program


def parse_apps_installer_linux(txt: str) -> dict[str, Any]:
    txts = txt.split("""yes '' | sed 3q; echo "----------------------------- installing """)
    res = {}
    for chunk in txts[1:]:
        try:
            k = chunk.split("----")[0].rstrip().lstrip()
            v = "\n".join(chunk.split("\n")[1:])
            res[k] = v
        except IndexError as e:
            print(f"""
❌ Error parsing chunk:
{"-" * 50}
{chunk}
{"-" * 50}""")
            raise e
    return res


def parse_apps_installer_windows(txt: str) -> dict[str, Any]:
    chunks: list[str] = []
    for idx, item in enumerate(txt.split(sep="winget install")):
        if idx == 0:
            continue
        if idx == 1:
            chunks.append(item)
        else:
            chunks.append("winget install" + item)
    # progs = L(txt.splitlines()).filter(lambda x: x.startswith("winget ") or x.startswith("#winget"))
    res: dict[str, str] = {}
    for a_chunk in chunks:
        try:
            name = a_chunk.split("--name ")[1]
            if "--Id" not in name:
                print(f"⚠️  Warning: {name} does not have an Id, skipping")
                continue
            name = name.split(" --Id ", maxsplit=1)[0].strip('"').strip('"')
            res[name] = a_chunk
        except IndexError as e:
            print(f"""
❌ Error parsing chunk:
{"-" * 50}
{a_chunk}
{"-" * 50}""")
            raise e
    return res


if __name__ == "__main__":
    pass
