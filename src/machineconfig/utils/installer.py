"""package manager"""

from machineconfig.utils.installer_utils.installer_abc import check_if_installed_already, parse_apps_installer_linux, parse_apps_installer_windows
from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import InstallerData, InstallerDataFiles, get_normalized_arch, get_os_name, OPERATING_SYSTEMS, CPU_ARCHITECTURES
from machineconfig.jobs.installer.package_groups import PACKAGE_GROUPS, PACKAGE_GROUP2NAMES
from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import INSTALL_VERSION_ROOT, LINUX_INSTALL_PATH
from machineconfig.utils.io import read_json

from rich.console import Console
from rich.panel import Panel
from typing import Any, Optional
import platform
from joblib import Parallel, delayed


def check_latest():
    console = Console()  # Added console initialization
    console.print(Panel("🔍  CHECKING FOR LATEST VERSIONS", title="Status", expand=False))  # Replaced print with Panel
    installers = get_installers(os=get_os_name(), arch=get_normalized_arch(), which_cats=["ESSENTIAL"])
    installers_github = []
    for inst__ in installers:
        app_name = inst__["appName"]
        repo_url = inst__["repoURL"]
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
        verdict, current_ver, new_ver = check_if_installed_already(exe_name=exe_name, version=version_to_be_installed, use_cache=False)
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
        console.print(f"\n[bold]{status.upper()}:[/bold]")
        console.rule(style="dim")
        for item in items:
            console.print(f"  {item['Tool']:<20} | Current: {item['Current Version']:<15} | New: {item['New Version']}")
    console.rule(style="dim")
    console.rule(style="bold blue")


def get_installed_cli_apps():
    print("🔍 LISTING INSTALLED CLI APPS 🔍")
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
    print(f"✅ Found {len(apps)} installed applications")
    return apps


def get_installers(os: OPERATING_SYSTEMS, arch: CPU_ARCHITECTURES, which_cats: Optional[list[PACKAGE_GROUPS]]) -> list[InstallerData]:
    res_all = get_all_installer_data_files()
    acceptable_apps_names: list[str] | None = None
    if which_cats is not None:
        acceptable_apps_names = []
        for cat in which_cats:
            acceptable_apps_names += PACKAGE_GROUP2NAMES[cat]
    else:
        acceptable_apps_names = None
    all_installers: list[InstallerData] = []
    for installer_data in res_all:
        if acceptable_apps_names is not None:
            if installer_data["appName"] not in acceptable_apps_names:
                continue
        if installer_data["fileNamePattern"][arch][os] is None:
            continue
        all_installers.append(installer_data)
    return all_installers


def get_all_installer_data_files() -> list[InstallerData]:
    import machineconfig.jobs.installer as module
    from pathlib import Path
    res_raw: InstallerDataFiles = read_json(Path(module.__file__).parent.joinpath("installer_data.json"))
    res_final: list[InstallerData] = res_raw["installers"]
    return res_final


def dynamically_extract_installers_system_groups_from_scripts():
    res_final: list[InstallerData] = []
    from platform import system
    if system() == "Windows":
        from machineconfig.setup_windows import APPS
        options_system = parse_apps_installer_windows(APPS.read_text(encoding="utf-8"))
    elif system() == "Linux" or system() == "Darwin":
        from machineconfig.setup_linux import APPS
        options_system = parse_apps_installer_linux(APPS.read_text(encoding="utf-8"))
    elif system() == "Darwin":
        from machineconfig.setup_mac import APPS
        options_system = parse_apps_installer_linux(APPS.read_text(encoding="utf-8"))
    else:
        raise NotImplementedError(f"❌ System {system()} not supported")
    os_name = get_os_name()
    for group_name, (docs, script) in options_system.items():
        item: InstallerData = {"appName": group_name, "doc": docs, "repoURL": "CMD", "fileNamePattern": {"amd64": {os_name: script}, "arm64": {os_name: script}}}
        res_final.append(item)
    return res_final


def install_bulk(installers_data: list[InstallerData], safe: bool = False, jobs: int = 10, fresh: bool = False):
    print("🚀 BULK INSTALLATION PROCESS 🚀")
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

    print(f"🚀 Starting installation of {len(installers_data)} packages...")
    print("📦 INSTALLING FIRST PACKAGE 📦")
    Installer(installers_data[0]).install(version=None)
    installers_remaining = installers_data[1:]
    print("📦 INSTALLING REMAINING PACKAGES 📦")

    # Use joblib for parallel processing of remaining installers
    res = Parallel(n_jobs=jobs)(delayed(lambda x: Installer(x).install_robust(version=None))(installer) for installer in installers_remaining)

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


def get_machineconfig_version() -> str:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version
    from pathlib import Path
    import tomllib

    name: str = "machineconfig"
    try:
        return _pkg_version(name)
    except PackageNotFoundError:
        pass
    root: Path = Path(__file__).resolve().parents[2]
    pyproject: Path = root / "pyproject.toml"
    if pyproject.is_file():
        with pyproject.open("rb") as f:
            data: dict[str, object] = tomllib.load(f)
        project = data.get("project")
        if isinstance(project, dict):
            version = project.get("version")
            if isinstance(version, str) and version:
                return version
    return "0.0.0"
