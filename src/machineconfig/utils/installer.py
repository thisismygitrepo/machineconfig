"""package manager"""

from machineconfig.utils.installer_utils.installer_abc import LINUX_INSTALL_PATH
from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import APP_INSTALLER_CATEGORY, InstallerData, InstallerDataFiles
from rich.console import Console
from rich.panel import Panel  # Added import

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import INSTALL_VERSION_ROOT
from machineconfig.utils.utils2 import read_json

from typing import Any
import platform
from joblib import Parallel, delayed


def check_latest():
    console = Console()  # Added console initialization
    console.print(Panel("🔍  CHECKING FOR LATEST VERSIONS", title="Status", expand=False))  # Replaced print with Panel
    installers = get_installers(system=platform.system(), dev=False)
    # installers += get_installers(system=platform.system(), dev=True)
    installers_github = []
    for inst__ in installers:
        app_name = inst__.installer_data.get("appName", "unknown")
        repo_url = inst__.installer_data.get("repoURL", "")
        if "ntop" in app_name:
            print(f"⏭️  Skipping {app_name} (ntop)")
            continue
        if "github" not in repo_url:
            print(f"⏭️  Skipping {app_name} (not a GitHub release)")
            continue
        installers_github.append(inst__)

    print(f"\n🔍 Checking {len(installers_github)} GitHub-based installers...\n")

    def func(inst: Installer):
        exe_name = inst.installer_data.get("exeName", "unknown")
        repo_url = inst.installer_data.get("repoURL", "")
        print(f"🔎 Checking {exe_name}...")
        _release_url, version_to_be_installed = inst.get_github_release(repo_url=repo_url, version=None)
        verdict, current_ver, new_ver = inst.check_if_installed_already(exe_name=exe_name, version=version_to_be_installed, use_cache=False)
        return exe_name, verdict, current_ver, new_ver

    print("\n⏳ Processing installers...\n")
    res = [func(inst) for inst in installers_github]

    print("\n📊 Generating results table...\n")

    # Convert to list of dictionaries and group by status
    result_data = []
    for tool, status, current_ver, new_ver in res:
        result_data.append({"Tool": tool, "Status": status, "Current Version": current_ver, "New Version": new_ver})

    # Group by status
    grouped_data: dict[str, list[dict[str, Any]]] = {}
    for item in result_data:
        status = item["Status"]
        if status not in grouped_data:
            grouped_data[status] = []
        grouped_data[status].append(item)

    console.print(Panel("📊  INSTALLATION STATUS SUMMARY", title="Status", expand=False))

    # Print each group
    for status, items in grouped_data.items():
        print(f"\n{status.upper()}:")
        print("-" * 60)
        for item in items:
            print(f"  {item['Tool']:<20} | Current: {item['Current Version']:<15} | New: {item['New Version']}")
    print("-" * 60)
    print(f"{'═' * 80}")


def get_installed_cli_apps():
    print(f"\n{'=' * 80}\n🔍 LISTING INSTALLED CLI APPS 🔍\n{'=' * 80}")
    if platform.system() == "Windows":
        print("🪟 Searching for Windows executables...")
        apps = PathExtended.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe", not_in=["notepad"])
    elif platform.system() in ["Linux", "Darwin"]:
        print(f"🐧 Searching for {platform.system()} executables...")
        if platform.system() == "Linux":
            apps = PathExtended(LINUX_INSTALL_PATH).search("*") + PathExtended("/usr/local/bin").search("*")
        else:  # Darwin/macOS
            apps = PathExtended("/usr/local/bin").search("*") + PathExtended("/opt/homebrew/bin").search("*")
    else:
        error_msg = f"❌ ERROR: System {platform.system()} not supported"
        print(error_msg)
        raise NotImplementedError(error_msg)
    apps = [app for app in apps if app.size("kb") > 0.1 and not app.is_symlink()]  # no symlinks like paint and wsl and bash
    print(f"✅ Found {len(apps)} installed applications\n{'=' * 80}")
    return apps


def get_installers(system: str, dev: bool) -> list[Installer]:
    print(f"\n{'=' * 80}\n🔍 LOADING INSTALLER CONFIGURATIONS 🔍\n{'=' * 80}")
    res_all = get_all_installer_data_files(system=system)
    if not dev:
        print("ℹ️  Excluding development installers...")
        del res_all["CUSTOM_DEV"]
        del res_all["OS_SPECIFIC_DEV"]
        del res_all["OS_GENERIC_DEV"]

    # Flatten the installer data from all categories
    all_installers: list[InstallerData] = []
    for _category, installer_data_files in res_all.items():
        all_installers.extend(installer_data_files["installers"])

    print(f"✅ Loaded {len(all_installers)} installer configurations\n{'=' * 80}")
    return [Installer(installer_data=installer_data) for installer_data in all_installers]


def get_all_installer_data_files(system: str) -> dict[APP_INSTALLER_CATEGORY, InstallerDataFiles]:
    print(f"\n{'=' * 80}\n📂 LOADING CONFIGURATION FILES 📂\n{'=' * 80}")

    print(f"🔍 Importing OS-specific installers for {system}...")
    if system == "Windows":
        import machineconfig.jobs.python_windows_installers as os_specific_installer
    else:
        import machineconfig.jobs.python_linux_installers as os_specific_installer

    print("🔍 Importing generic installers...")
    import machineconfig.jobs.python_generic_installers as generic_installer

    path_os_specific = PathExtended(os_specific_installer.__file__).parent
    path_os_generic = PathExtended(generic_installer.__file__).parent

    path_os_specific_dev = path_os_specific.joinpath("dev")
    path_os_generic_dev = path_os_generic.joinpath("dev")

    print("📂 Loading configuration files...")
    res_final: dict[APP_INSTALLER_CATEGORY, InstallerDataFiles] = {}

    print(f"""📄 Loading OS-specific config from: {path_os_specific.joinpath("config.json")}""")
    os_specific_data = read_json(path=path_os_specific.joinpath("config.json"))
    res_final["OS_SPECIFIC"] = InstallerDataFiles(os_specific_data)

    print(f"""📄 Loading OS-generic config from: {path_os_generic.joinpath("config.json")}""")
    os_generic_data = read_json(path=path_os_generic.joinpath("config.json"))
    res_final["OS_GENERIC"] = InstallerDataFiles(os_generic_data)

    print(f"""📄 Loading OS-specific dev config from: {path_os_specific_dev.joinpath("config.json")}""")
    os_specific_dev_data = read_json(path=path_os_specific_dev.joinpath("config.json"))
    res_final["OS_SPECIFIC_DEV"] = InstallerDataFiles(os_specific_dev_data)

    print(f"""📄 Loading OS-generic dev config from: {path_os_generic_dev.joinpath("config.json")}""")
    os_generic_dev_data = read_json(path=path_os_generic_dev.joinpath("config.json"))
    res_final["OS_GENERIC_DEV"] = InstallerDataFiles(os_generic_dev_data)

    path_custom_installer = path_os_generic.with_name("python_custom_installers")
    path_custom_installer_dev = path_custom_installer.joinpath("dev")

    print(f"🔍 Loading custom installers from: {path_custom_installer}")
    import runpy

    res_custom_installers: list[InstallerData] = []
    for item in path_custom_installer.search("*.py", r=False, not_in=["__init__"]):
        try:
            print(f"📄 Loading custom installer: {item.name}")
            installer_data: InstallerData = runpy.run_path(str(item), run_name=None)["config_dict"]
            res_custom_installers.append(installer_data)
        except Exception as ex:
            print(f"❌ Failed to load {item}: {ex}")

    print(f"🔍 Loading custom dev installers from: {path_custom_installer_dev}")
    res_custom_dev_installers: list[InstallerData] = []
    for item in path_custom_installer_dev.search("*.py", r=False, not_in=["__init__"]):
        try:
            print(f"📄 Loading custom dev installer: {item.name}")
            installer_data: InstallerData = runpy.run_path(str(item), run_name=None)["config_dict"]
            res_custom_dev_installers.append(installer_data)
        except Exception as ex:
            print(f"❌ Failed to load {item}: {ex}")

    res_final["CUSTOM"] = InstallerDataFiles({"version": "1", "installers": res_custom_installers})
    res_final["CUSTOM_DEV"] = InstallerDataFiles({"version": "1", "installers": res_custom_dev_installers})

    print(
        f"✅ Configuration loading complete:\n - OS_SPECIFIC: {len(res_final['OS_SPECIFIC']['installers'])} items\n - OS_GENERIC: {len(res_final['OS_GENERIC']['installers'])} items\n - CUSTOM: {len(res_final['CUSTOM']['installers'])} items\n{'=' * 80}"
    )
    return res_final


def install_all(installers: list[Installer], safe: bool = False, jobs: int = 10, fresh: bool = False):
    print(f"\n{'=' * 80}\n🚀 BULK INSTALLATION PROCESS 🚀\n{'=' * 80}")
    if fresh:
        print("🧹 Fresh install requested - clearing version cache...")
        PathExtended(INSTALL_VERSION_ROOT).delete(sure=True)
        print("✅ Version cache cleared")

    if safe:
        pass
        # print("⚠️  Safe installation mode activated...")
        # from machineconfig.jobs.python.check_installations import APP_SUMMARY_PATH
        # if platform.system().lower() == "windows":
        #     print("🪟 Moving applications to Windows Apps folder...")
        #     # PathExtended.get_env().WindowsPaths().WindowsApps)
        #     folder = PathExtended.home().joinpath("AppData/Local/Microsoft/WindowsApps")
        #     apps_dir.search("*").apply(lambda app: app.move(folder=folder))
        # elif platform.system().lower() in ["linux", "darwin"]:
        #     system_name = "Linux" if platform.system().lower() == "linux" else "macOS"
        #     print(f"🐧 Moving applications to {system_name} bin folder...")
        #     if platform.system().lower() == "linux":
        #         install_path = LINUX_INSTALL_PATH
        #     else:  # Darwin/macOS
        #         install_path = "/usr/local/bin"
        #     Terminal().run(f"sudo mv {apps_dir.as_posix()}/* {install_path}/").capture().print_if_unsuccessful(desc=f"MOVING executable to {install_path}", strict_err=True, strict_returncode=True)
        # else:
        #     error_msg = f"❌ ERROR: System {platform.system()} not supported"
        #     print(error_msg)
        #     raise NotImplementedError(error_msg)

        # apps_dir.delete(sure=True)
        # print(f"✅ Safe installation completed\n{'='*80}")
        # return None

    print(f"🚀 Starting installation of {len(installers)} packages...")
    print(f"\n{'=' * 80}\n📦 INSTALLING FIRST PACKAGE 📦\n{'=' * 80}")
    installers[0].install(version=None)
    installers_remaining = installers[1:]
    print(f"\n{'=' * 80}\n📦 INSTALLING REMAINING PACKAGES 📦\n{'=' * 80}")

    # Use joblib for parallel processing of remaining installers
    res = Parallel(n_jobs=jobs)(delayed(lambda x: x.install_robust(version=None))(installer) for installer in installers_remaining)

    console = Console()

    print("\n")
    console.rule("📊 INSTALLATION RESULTS SUMMARY 📊")

    print("\n")
    console.rule("✓ Same Version Apps")
    same_version_results = [r for r in res if r and "same version" in str(r)]
    for result in same_version_results:
        print(f"  {result}")

    print("\n")
    console.rule("⬆️ Updated Apps")
    updated_results = [r for r in res if r and "updated from" in str(r)]
    for result in updated_results:
        print(f"  {result}")

    print("\n")
    console.rule("❌ Failed Apps")
    failed_results = [r for r in res if r and "Failed at" in str(r)]
    for result in failed_results:
        print(f"  {result}")

    print("\n")
    print("✨ INSTALLATION COMPLETE ✨".center(100, "="))
    print("\n" * 2)


if __name__ == "__main__":
    pass
