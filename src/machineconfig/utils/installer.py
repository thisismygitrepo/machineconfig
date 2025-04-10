"""package manager
"""
from machineconfig.utils.installer_utils.installer_abc import LINUX_INSTALL_PATH, CATEGORY
from machineconfig.utils.installer_utils.installer_class import Installer
from rich.console import Console

from crocodile.file_management import P, Read
from crocodile.core import List as L
from crocodile.meta import Terminal
from machineconfig.utils.utils import INSTALL_VERSION_ROOT

# from dataclasses import dataclass
from typing import Any
import platform


def check_latest():
    print(f"""
╔{'═'*78}╗
║ 🔍  CHECKING FOR LATEST VERSIONS                                               ║
╚{'═'*78}╝
""")
    installers = get_installers(system=platform.system(), dev=False)
    # installers += get_installers(system=platform.system(), dev=True)
    installers_gitshub = []
    for inst__ in installers:
        if "ntop" in inst__.name: 
            print(f"⏭️  Skipping {inst__.name} (ntop)")
            continue
        if "github" not in inst__.repo_url:
            print(f"⏭️  Skipping {inst__.name} (not a GitHub release)")
            continue
        installers_gitshub.append(inst__)
        
    print(f"\n🔍 Checking {len(installers_gitshub)} GitHub-based installers...\n")

    def func(inst: Installer):
        print(f"🔎 Checking {inst.exe_name}...")
        _release_url, version_to_be_installed = inst.get_github_release(repo_url=inst.repo_url, version=None)
        verdict, current_ver, new_ver = inst.check_if_installed_already(exe_name=inst.exe_name, version=version_to_be_installed, use_cache=False)
        return inst.exe_name, verdict, current_ver, new_ver

    print("\n⏳ Processing installers...\n")
    res = L(installers_gitshub).apply(func=func, jobs=1)
    
    import pandas as pd
    print("\n📊 Generating results table...\n")
    res_df = pd.DataFrame(res, columns=["Tool", "Status", "Current Version", "New Version"]).groupby("Status").apply(lambda x: x).reset_index(drop=True)
    
    from crocodile.core import Display
    Display.set_pandas_display()
    print(f"""
╔{'═'*78}╗
║ 📊  INSTALLATION STATUS SUMMARY                                                ║
╚{'═'*78}╝
""")
    print(res_df)
    print(f"{'═'*80}")


def get_installed_cli_apps():
    print(f"\n{'='*80}\n🔍 LISTING INSTALLED CLI APPS 🔍\n{'='*80}")
    if platform.system() == "Windows": 
        print("🪟 Searching for Windows executables...")
        apps = P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe", not_in=["notepad"])
    elif platform.system() == "Linux": 
        print("🐧 Searching for Linux executables...")
        apps = P(LINUX_INSTALL_PATH).search("*") + P("/usr/local/bin").search("*")
    else: 
        error_msg = f"❌ ERROR: System {platform.system()} not supported"
        print(error_msg)
        raise NotImplementedError(error_msg)
        
    apps = L([app for app in apps if app.size("kb") > 0.1 and not app.is_symlink()])  # no symlinks like paint and wsl and bash
    print(f"✅ Found {len(apps)} installed applications\n{'='*80}")
    return apps


def get_installers(system: str, dev: bool) -> list[Installer]:
    print(f"\n{'='*80}\n🔍 LOADING INSTALLER CONFIGURATIONS 🔍\n{'='*80}")
    res_all = get_all_dicts(system=system)
    if not dev:
        print("ℹ️  Excluding development installers...")
        del res_all["CUSTOM_DEV"]
        del res_all["OS_SPECIFIC_DEV"]
        del res_all["OS_GENERIC_DEV"]
    res_final = {}
    for _k, v in res_all.items():
        res_final.update(v)
    print(f"✅ Loaded {len(res_final)} installer configurations\n{'='*80}")
    return [Installer.from_dict(d=vd, name=k) for k, vd in res_final.items()]


def get_all_dicts(system: str) -> dict[CATEGORY, dict[str, dict[str, Any]]]:
    print(f"\n{'='*80}\n📂 LOADING CONFIGURATION FILES 📂\n{'='*80}")
    
    print(f"🔍 Importing OS-specific installers for {system}...")
    if system == "Windows": 
        import machineconfig.jobs.python_windows_installers as os_specific_installer
    else: 
        import machineconfig.jobs.python_linux_installers as os_specific_installer

    print("🔍 Importing generic installers...")
    import machineconfig.jobs.python_generic_installers as generic_installer
    path_os_specific = P(os_specific_installer.__file__).parent
    path_os_generic = P(generic_installer.__file__).parent

    path_os_specific_dev = path_os_specific.joinpath("dev")
    path_os_generic_dev = path_os_generic.joinpath("dev")

    print("📂 Loading configuration files...")
    res_final: dict[CATEGORY, dict[str, dict[str, Any]]] = {}
    print(f"""📄 Loading OS-specific config from: {path_os_specific.joinpath('config.json')}""")
    res_final["OS_SPECIFIC"] = Read.json(path=path_os_specific.joinpath("config.json"))

    print(f"""📄 Loading OS-generic config from: {path_os_generic.joinpath("config.json")}""")
    res_final["OS_GENERIC"] = Read.json(path=path_os_generic.joinpath("config.json"))
    
    print(f"""📄 Loading OS-specific dev config from: {path_os_specific_dev.joinpath("config.json")}""")
    res_final["OS_SPECIFIC_DEV"] = Read.json(path=path_os_specific_dev.joinpath("config.json"))
    
    print(f"""📄 Loading OS-generic dev config from: {path_os_generic_dev.joinpath("config.json")}""")
    res_final["OS_GENERIC_DEV"] = Read.json(path=path_os_generic_dev.joinpath("config.json"))

    path_custom_installer = path_os_generic.with_name("python_custom_installers")
    path_custom_installer_dev = path_custom_installer.joinpath("dev")

    print(f"🔍 Loading custom installers from: {path_custom_installer}")
    import runpy
    res_custom: dict[str, dict[str, Any]] = {}
    for item in path_custom_installer.search("*.py", r=False, not_in=["__init__"]):
        try:
            print(f"📄 Loading custom installer: {item.name}")
            config_dict = runpy.run_path(str(item), run_name=None)['config_dict']
            res_custom[item.stem] = config_dict
        except Exception as ex:
            print(f"❌ Failed to load {item}: {ex}")

    print(f"🔍 Loading custom dev installers from: {path_custom_installer_dev}")
    res_custom_dev: dict[str, dict[str, Any]] = {}
    for item in path_custom_installer_dev.search("*.py", r=False, not_in=["__init__"]):
        try:
            print(f"📄 Loading custom dev installer: {item.name}")
            config_dict = runpy.run_path(str(item), run_name=None)['config_dict']
            res_custom_dev[item.stem] = config_dict
        except Exception as ex:
            print(f"❌ Failed to load {item}: {ex}")

    res_final["CUSTOM"] = res_custom
    res_final["CUSTOM_DEV"] = res_custom_dev
    
    print(f"✅ Configuration loading complete:\n - OS_SPECIFIC: {len(res_final['OS_SPECIFIC'])} items\n - OS_GENERIC: {len(res_final['OS_GENERIC'])} items\n - CUSTOM: {len(res_final['CUSTOM'])} items\n{'='*80}")
    return res_final


def install_all(installers: L[Installer], safe: bool=False, jobs: int = 10, fresh: bool=False):
    print(f"\n{'='*80}\n🚀 BULK INSTALLATION PROCESS 🚀\n{'='*80}")
    if fresh: 
        print("🧹 Fresh install requested - clearing version cache...")
        INSTALL_VERSION_ROOT.delete(sure=True)
        print("✅ Version cache cleared")
        
    if safe:
        print("⚠️  Safe installation mode activated...")
        from machineconfig.jobs.python.check_installations import APP_SUMMARY_PATH
        apps_dir = APP_SUMMARY_PATH.readit()
        
        if platform.system().lower() == "windows":
            print("🪟 Moving applications to Windows Apps folder...")
            apps_dir.search("*").apply(lambda app: app.move(folder=P.get_env().WindowsPaths().WindowsApps))
        elif platform.system().lower() == "linux":
            print("🐧 Moving applications to Linux bin folder...")
            Terminal().run(f"sudo mv {apps_dir.as_posix()}/* {LINUX_INSTALL_PATH}/").capture().print_if_unsuccessful(desc=f"MOVING executable to {LINUX_INSTALL_PATH}", strict_err=True, strict_returncode=True)
        else: 
            error_msg = f"❌ ERROR: System {platform.system()} not supported"
            print(error_msg)
            raise NotImplementedError(error_msg)
            
        apps_dir.delete(sure=True)
        print(f"✅ Safe installation completed\n{'='*80}")
        return None
        
    print(f"🚀 Starting installation of {len(installers)} packages...")
    print(f"\n{'='*80}\n📦 INSTALLING FIRST PACKAGE 📦\n{'='*80}")
    installers.list[0].install(version=None)
    
    print(f"\n{'='*80}\n📦 INSTALLING REMAINING PACKAGES 📦\n{'='*80}")
    res = installers.slice(start=1).apply(lambda x: x.install_robust(version=None), jobs=jobs)  # try out the first installer alone cause it will ask for password, so the rest will inherit the sudo session.
    console = Console()
    
    print("\n")
    console.rule("📊 INSTALLATION RESULTS SUMMARY 📊")
    
    print("\n")
    console.rule("✓ Same Version Apps")
    print(f"{res.filter(lambda x: 'same version' in x).print()}")
    
    print("\n")
    console.rule("⬆️ Updated Apps")
    print(f"{res.filter(lambda x: 'updated from' in x).print()}")
    
    print("\n")
    console.rule("❌ Failed Apps")
    print(f"{res.filter(lambda x: 'Failed at' in x).print()}")

    print("\n")
    print("✨ INSTALLATION COMPLETE ✨".center(100, "="))
    print("\n" * 2)


if __name__ == "__main__":
    pass
