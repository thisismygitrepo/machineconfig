from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH, LINUX_INSTALL_PATH
from typing import Optional
import subprocess


def find_move_delete_windows(downloaded_file_path: PathExtended, exe_name: Optional[str] = None, delete: bool = True, rename_to: Optional[str] = None):
    print(f"\n{'=' * 80}\n🔍 PROCESSING WINDOWS EXECUTABLE 🔍\n{'=' * 80}")
    if exe_name is not None and ".exe" in exe_name:
        exe_name = exe_name.replace(".exe", "")
    if downloaded_file_path.is_file():
        exe = downloaded_file_path
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded_file_path}")
        if exe_name is None:
            exe = downloaded_file_path.search("*.exe", r=True)[0]
            print(f"✅ Found executable: {exe}")
        else:
            tmp = downloaded_file_path.search(f"{exe_name}.exe", r=True)
            if len(tmp) == 1:
                exe = tmp[0]
                print(f"✅ Found exact match for {exe_name}.exe: {exe}")
            else:
                search_res = downloaded_file_path.search("*.exe", r=True)
                if len(search_res) == 0:
                    print(f"❌ ERROR: No executable found in {downloaded_file_path}")
                    raise IndexError(f"No executable found in {downloaded_file_path}")
                elif len(search_res) == 1:
                    exe = search_res[0]
                    print(f"✅ Found single executable: {exe}")
                else:
                    exe = max(search_res, key=lambda x: x.size("kb"))
                    print(f"✅ Selected largest executable ({exe.size('kb')} KB): {exe}")
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


def find_move_delete_linux(downloaded: PathExtended, tool_name: str, delete: Optional[bool] = True, rename_to: Optional[str] = None):
    print(f"\n{'=' * 80}\n🔍 PROCESSING LINUX EXECUTABLE 🔍\n{'=' * 80}")
    if downloaded.is_file():
        exe = downloaded
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded}")
        res = downloaded.search(f"*{tool_name}*", folders=False, r=True)
        if len(res) == 1:
            exe = res[0]
            print(f"✅ Found match for pattern '*{tool_name}*': {exe}")
        else:
            exe_search_res = downloaded.search(tool_name, folders=False, r=True)
            if len(exe_search_res) == 0:
                print(f"❌ ERROR: No search results for `{tool_name}` in `{downloaded}`")
                raise IndexError(f"No executable found in {downloaded}")
            elif len(exe_search_res) == 1:
                exe = exe_search_res[0]
                print(f"✅ Found exact match for '{tool_name}': {exe}")
            else:
                exe = max(exe_search_res, key=lambda x: x.size("kb"))
                print(f"✅ Selected largest executable ({exe.size('kb')} KB): {exe}")

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
    print(f"✅ Executable installed at: {exe_new_location}\n{'=' * 80}")
    return exe_new_location
