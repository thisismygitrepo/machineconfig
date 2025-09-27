"""Devops Devapps Install"""

# import subprocess
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from machineconfig.utils.source_of_truth import LIBRARY_ROOT
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.installer import get_installers, install_all
from machineconfig.utils.schemas.installer.installer_types import get_normalized_arch, get_os_name
from platform import system
from typing import Any, Optional, Literal, TypeAlias, get_args, Annotated

WHICH_CAT: TypeAlias = Literal["essentials", "essentialsDev", "systymPackages", "precheckedPackages"]


def main_with_parser():
    import typer
    app = typer.Typer()
    app.command()(main)
    app()


def main(which: Annotated[Optional[str], typer.Argument(help=f"Choose a category or program to install, {list(get_args(WHICH_CAT))} or <program_name>")]) -> None:
    if which is not None and which in get_args(WHICH_CAT):  # install by category
        return get_programs_by_category(program_name=which)  # type: ignore

    if which is not None:  # install by name
        total_messages: list[str] = []
        for a_which in which.split(",") if type(which) == str else which:
            all_installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["GITHUB_ESSENTIAL", "CUSTOM_ESSENTIAL", "GITHUB_DEV", "CUSTOM_DEV"])

            # Find installer by exe_name or name
            selected_installer = None
            for installer in all_installers:
                exe_name = installer.installer_data.get("exeName", "")
                app_name = installer.installer_data.get("appName", "")
                if exe_name == a_which or app_name == a_which:
                    selected_installer = installer
                    break

            if selected_installer is None:
                available_names = [f"{inst.installer_data.get('exeName', 'unknown')} ({inst.installer_data.get('appName', 'unknown')})" for inst in all_installers[:10]]  # Show first 10
                raise ValueError(f"{a_which=} not found. Available installers include: {available_names}")

            print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🔧 Installing: {a_which}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            print(selected_installer)
            message = selected_installer.install_robust(version=None)  # finish the task
            total_messages.append(message)
        for a_message in total_messages:
            print(a_message)
        return None

    installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["GITHUB_ESSENTIAL", "CUSTOM_ESSENTIAL", "GITHUB_DEV", "CUSTOM_DEV"])
    # Check installed programs with progress indicator
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("✅ Checking installed programs...", total=len(installers))
        installer_options = []
        for x in installers:
            installer_options.append(x.get_description())
            progress.update(task, advance=1)

    # Add category options at the beginning for better visibility
    category_options = [f"📦 {cat}" for cat in get_args(WHICH_CAT)]
    options = category_options + ["─" * 50] + installer_options
    
    program_names = choose_from_options(multi=True, msg="Categories are prefixed with 📦", options=options, header="🚀 CHOOSE DEV APP OR CATEGORY", default="📦 essentials", fzf=True)

    total_commands = ""
    installation_messages: list[str] = []
    for _an_idx, a_program_name in enumerate(program_names):
        # Skip separator lines
        if a_program_name.startswith("─"):
            continue
            
        print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🔄 Processing: {a_program_name}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
        
        # Handle category options (remove emoji prefix)
        if a_program_name.startswith("📦 "):
            category_name = a_program_name[2:]  # Remove "📦 " prefix
            if category_name in get_args(WHICH_CAT):
                shell_commands = get_programs_by_category(program_name=category_name)  # type: ignore
                total_commands += "\n" + shell_commands
        else:
            # Handle individual installer options
            installer_idx = installer_options.index(a_program_name)
            an_installer = installers[installer_idx]
            status_message = an_installer.install_robust(version=None)  # finish the task - this returns a status message, not a command
            installation_messages.append(status_message)

    # Print all installation status messages
    print("\n📊 INSTALLATION SUMMARY:")
    print("=" * 50)
    for message in installation_messages:
        print(message)

    # Only run shell commands if there are any (from category installations)
    if total_commands.strip():
        import subprocess

        print("\n🚀 Running additional shell commands...")
        subprocess.run(total_commands, shell=True, check=True)


def get_programs_by_category(program_name: WHICH_CAT):
    print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📦 Installing Category: {program_name}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    match program_name:
        case "essentials":
            installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["GITHUB_ESSENTIAL", "CUSTOM_ESSENTIAL"])
            install_all(installers=installers_)
            program = ""
        case "essentialsDev":
            installers_ = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["GITHUB_DEV", "CUSTOM_DEV", "GITHUB_ESSENTIAL", "CUSTOM_ESSENTIAL"])
            install_all(installers=installers_)
            program = ""
        case "systymPackages":
            if system() == "Windows":
                options_system = parse_apps_installer_windows(LIBRARY_ROOT.joinpath("setup_windows/apps.ps1").read_text(encoding="utf-8"))
            elif system() == "Linux":
                options_system_1 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps_dev.sh").read_text(encoding="utf-8"))
                options_system_2 = parse_apps_installer_linux(LIBRARY_ROOT.joinpath("setup_linux/apps.sh").read_text(encoding="utf-8"))
                options_system = {**options_system_1, **options_system_2}
            else:
                raise NotImplementedError(f"❌ System {system()} not supported")
            program_names = choose_from_options(multi=True, msg="", options=sorted(list(options_system.keys())), header="🚀 CHOOSE DEV APP", fzf=True)
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
        # case "CHOOSE": raise NotImplementedError("CHOOSE is not implemented yet.")
        # case "OtherDevApps":
        #     installers = get_installers(dev=True, system=system())
        #     options__: list[str] = [x.get_description() for x in tqdm(installers, desc="Checking installed programs")]
        #     program_names = choose_from_options(multi=True, msg="", options=sorted(options__) + ["all"], header="CHOOSE DEV APP")
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

        case "precheckedPackages":
            # from machineconfig.jobs.python.check_installations import precheckedPackages
            # ci = precheckedPackages()
            # ci.download_safe_apps(name="essentials")
            # program = ""
            raise NotImplementedError("precheckedPackages is not implemented yet.")
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
