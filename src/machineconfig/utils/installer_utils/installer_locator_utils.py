from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH, LINUX_INSTALL_PATH, INSTALL_VERSION_ROOT

from pathlib import Path
from typing import Optional
import subprocess
import platform


def find_move_delete_windows(downloaded_file_path: PathExtended, tool_name: Optional[str], delete: bool, rename_to: Optional[str]):
    # print("🔍 PROCESSING WINDOWS EXECUTABLE 🔍")
    # if exe_name is not None and len(exe_name.split("+")) > 1:
    #     last_result = None
    #     for a_binary in [x.strip() for x in exe_name.split("+") if x.strip() != ""]:
    #         last_result = find_move_delete_windows(downloaded_file_path=downloaded_file_path, exe_name=a_binary, delete=delete, rename_to=rename_to)
    #     return last_result
    if tool_name is not None and ".exe" in tool_name:
        tool_name = tool_name.replace(".exe", "")
    if downloaded_file_path.is_file():
        exe = downloaded_file_path
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded_file_path}")
        if tool_name is None:
            exe = list(downloaded_file_path.rglob("*.exe"))[0]
            print(f"✅ Found executable: {exe}")
        else:
            tmp = list(downloaded_file_path.rglob(f"{tool_name}.exe"))
            if len(tmp) == 1:
                exe = tmp[0]
                print(f"✅ Found exact match for {tool_name}.exe: {exe}")
            else:
                search_res = list(downloaded_file_path.rglob("*.exe"))
                if len(search_res) == 0:
                    print(f"❌ ERROR: No executable found in {downloaded_file_path}")
                    raise IndexError(f"No executable found in {downloaded_file_path}")
                elif len(search_res) == 1:
                    exe = search_res[0]
                    print(f"✅ Found single executable: {exe}")
                else:
                    exe = max(search_res, key=lambda x: x.stat().st_size)
                    print(f"✅ Selected largest executable ({round(exe.stat().st_size / 1024, 1)} KB): {exe}")
        if rename_to and exe.name != rename_to:
            print(f"🏷️  Renaming '{exe.name}' to '{rename_to}'")
            exe = exe.with_name(name=rename_to, inplace=True)

    print(f"📦 Moving executable to: {WINDOWS_INSTALL_PATH}")
    exe_new_location = exe.move(folder=WINDOWS_INSTALL_PATH, overwrite=True)  # latest version overwrites older installation.
    print(f"✅ Executable installed at: {exe_new_location}")

    if delete:
        print("🗑️  Cleaning up temporary files...")
        downloaded_file_path.delete(sure=True)
        print("✅ Temporary files removed")

    print(f"{'=' * 80}")
    return exe_new_location


def find_move_delete_linux(downloaded: PathExtended, tool_name: Optional[str], delete: bool, rename_to: Optional[str]):
    # if len(tool_name.split("+")) > 1:
    #     last_result = None
    #     for a_binary in [x.strip() for x in tool_name.split("+") if x.strip() != ""]:
    #         last_result = find_move_delete_linux(downloaded=downloaded, tool_name=a_binary, delete=False, rename_to=rename_to)
    #     return last_result

    print("🔍 PROCESSING LINUX EXECUTABLE 🔍")
    if downloaded.is_file():
        exe = downloaded
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded}")
        res = [p for p in downloaded.rglob(f"*{tool_name}*") if p.is_file()]
        if len(res) == 1:
            exe = res[0]
            print(f"✅ Found match for pattern '*{tool_name}*': {exe}")
        else:
            if tool_name is None:  # no tool name provided, get the largest executable
                search_res = [p for p in downloaded.rglob("*") if p.is_file()]
                if len(search_res) == 0:
                    print(f"❌ ERROR: No search results in `{downloaded}`")
                    raise IndexError(f"No executable found in {downloaded}")
                exe = max(search_res, key=lambda x: x.stat().st_size)
                print(f"✅ Selected largest executable ({round(exe.stat().st_size / 1024, 1)} KB): {exe}")
            else:
                exe_search_res = [p for p in downloaded.rglob(tool_name) if p.is_file()]
                if len(exe_search_res) == 0:
                    print(f"❌ ERROR: No search results for `{tool_name}` in `{downloaded}`")
                    raise IndexError(f"No executable found in {downloaded}")
                elif len(exe_search_res) == 1:
                    exe = exe_search_res[0]
                    print(f"✅ Found exact match for '{tool_name}': {exe}")
                else:
                    exe = max(exe_search_res, key=lambda x: x.stat().st_size)
                    print(f"✅ Selected largest executable ({round(exe.stat().st_size / 1024, 1)} KB): {exe}")

    if rename_to and exe.name != rename_to:
        print(f"🏷️  Renaming '{exe.name}' to '{rename_to}'")
        exe = exe.with_name(name=rename_to, inplace=True)

    print("🔐 Setting executable permissions (chmod 777)...")
    exe.chmod(0o777)

    print(f"📦 Moving executable to: {LINUX_INSTALL_PATH}")
    # exe.move(folder=LINUX_INSTALL_PATH, overwrite=False)
    if "/usr" in LINUX_INSTALL_PATH:
        print("🔑 Using sudo to move file to system directory...")
        cmd = f"sudo mv {exe} {LINUX_INSTALL_PATH}/"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        success = result.returncode == 0 and result.stderr == ""
        if not success:
            desc = f"MOVING executable `{exe}` to {LINUX_INSTALL_PATH}"
            print(f"❌ {desc} failed")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            print(f"Return code: {result.returncode}")
            raise RuntimeError(f"Failed to move executable: {result.stderr or result.stdout}")
    else:
        exe.move(folder=LINUX_INSTALL_PATH, overwrite=True)

    if delete:
        print("🗑️  Cleaning up temporary files...")
        downloaded.delete(sure=True)
        print("✅ Temporary files removed")

    exe_new_location = PathExtended(LINUX_INSTALL_PATH).joinpath(exe.name)
    print(f"✅ Executable installed at: {exe_new_location}")
    return exe_new_location


def check_tool_exists(tool_name: str) -> bool:
    if platform.system() == "Windows":
        tool_name_exe = tool_name.replace(".exe", "") + ".exe"
        res1 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name_exe).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name_exe).is_file()])
        if res1:
            return True
        tool_name_no_exe = tool_name.replace(".exe", "")
        res2 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name_no_exe).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name_no_exe).is_file()])
        return res2
    elif platform.system() in ["Linux", "Darwin"]:
        root_path = Path(LINUX_INSTALL_PATH)
        standard_checks = [
            Path("/usr/local/bin").joinpath(tool_name).is_file(),
            Path("/usr/bin").joinpath(tool_name).is_file(),
            root_path.joinpath(tool_name).is_file()
        ]
        if any(standard_checks):
            return True
        # Check for npm packages via nvm
        npm_check = False
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
            version = result.stdout.strip().lstrip('v')
            nvm_bin_path = Path.home() / ".nvm" / "versions" / "node" / f"v{version}" / "bin" / tool_name
            npm_check = nvm_bin_path.is_file()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return npm_check
    else:
        raise NotImplementedError(f"platform {platform.system()} not implemented")

def is_executable_in_path(name: str) -> bool:
    import os
    path_dirs = os.environ['PATH'].split(os.pathsep)
    for path_dir in path_dirs:
        path_to_executable = os.path.join(path_dir, name)
        if os.path.isfile(path_to_executable) and os.access(path_to_executable, os.X_OK): return True
    return False


def check_if_installed_already(exe_name: str, version: Optional[str], use_cache: bool) -> tuple[str, str, str]:
    print(f"🔍 CHECKING INSTALLATION STATUS: {exe_name} 🔍")
    INSTALL_VERSION_ROOT.joinpath(exe_name).parent.mkdir(parents=True, exist_ok=True)
    tmp_path = INSTALL_VERSION_ROOT.joinpath(exe_name)

    if use_cache:
        print("🗂️  Using cached version information...")
        if tmp_path.exists():
            existing_version = tmp_path.read_text(encoding="utf-8").rstrip()
            print(f"📄 Found cached version: {existing_version}")
        else:
            existing_version = None
            print("ℹ️  No cached version information found")
    else:
        print("🔍 Checking installed version directly...")
        result = subprocess.run([exe_name, "--version"], check=False, capture_output=True, text=True)
        if result.stdout.strip() == "":
            existing_version = None
            print("ℹ️  Could not detect installed version")
        else:
            existing_version = result.stdout.strip()
            print(f"📄 Detected installed version: {existing_version}")

    if existing_version is not None and version is not None:
        if existing_version == version:
            print(f"✅ {exe_name} is up to date (version {version})")
            print(f"📂 Version information stored at: {INSTALL_VERSION_ROOT}")
            return ("✅ Up to date", version.strip(), version.strip())
        else:
            print(f"🔄 {exe_name} needs update: {existing_version.rstrip()} → {version}")
            tmp_path.write_text(version, encoding="utf-8")
            return ("❌ Outdated", existing_version.strip(), version.strip())
    else:
        print(f"📦 {exe_name} is not installed. Will install version: {version}")
        # tmp_path.write_text(version, encoding="utf-8")

    print(f"{'=' * 80}")
    return ("⚠️ NotInstalled", "None", version or "unknown")


