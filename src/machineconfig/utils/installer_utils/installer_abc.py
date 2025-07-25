from crocodile.file_management import P
from crocodile.meta import Terminal
from typing import Optional, TypeAlias, Literal

# LINUX_INSTALL_PATH = '/usr/local/bin'
# LINUX_INSTALL_PATH = '~/.local/bin'
LINUX_INSTALL_PATH = P.home().joinpath(".local/bin").__str__()
WINDOWS_INSTALL_PATH = P.home().joinpath("AppData/Local/Microsoft/WindowsApps").__str__()
CATEGORY: TypeAlias = Literal["OS_SPECIFIC", "OS_GENERIC", "CUSTOM", "OS_SPECIFIC_DEV", "OS_GENERIC_DEV", "CUSTOM_DEV"]


def find_move_delete_windows(downloaded_file_path: P, exe_name: Optional[str] = None, delete: bool=True, rename_to: Optional[str] = None):
    print(f"\n{'='*80}\n🔍 PROCESSING WINDOWS EXECUTABLE 🔍\n{'='*80}")
    if exe_name is not None and ".exe" in exe_name: exe_name = exe_name.replace(".exe", "")
    if downloaded_file_path.is_file():
        exe = downloaded_file_path
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded_file_path}")
        if exe_name is None:
            exe = downloaded_file_path.search("*.exe", r=True).list[0]
            print(f"✅ Found executable: {exe}")
        else:
            tmp = downloaded_file_path.search(f"{exe_name}.exe", r=True)
            if len(tmp) == 1:
                exe = tmp.list[0]
                print(f"✅ Found exact match for {exe_name}.exe: {exe}")
            else:
                search_res = downloaded_file_path.search("*.exe", r=True)
                if len(search_res) == 0:
                    print(f"❌ ERROR: No executable found in {downloaded_file_path}")
                    raise IndexError(f"No executable found in {downloaded_file_path}")
                elif len(search_res) == 1:
                    exe = search_res.list[0]
                    print(f"✅ Found single executable: {exe}")
                else:
                    exe = search_res.sort(lambda x: x.size("kb")).list[-1]
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

    print(f"{'='*80}")
    return exe_new_location


def find_move_delete_linux(downloaded: P, tool_name: str, delete: Optional[bool] = True, rename_to: Optional[str] = None):
    print(f"\n{'='*80}\n🔍 PROCESSING LINUX EXECUTABLE 🔍\n{'='*80}")
    if downloaded.is_file():
        exe = downloaded
        print(f"📄 Found direct executable file: {exe}")
    else:
        print(f"🔎 Searching for executable in: {downloaded}")
        res = downloaded.search(f"*{tool_name}*", folders=False, r=True)
        if len(res) == 1:
            exe = res.list[0]
            print(f"✅ Found match for pattern '*{tool_name}*': {exe}")
        else:
            exe_search_res = downloaded.search(tool_name, folders=False, r=True)
            if len(exe_search_res) == 0:
                print(f"❌ ERROR: No search results for `{tool_name}` in `{downloaded}`")
                raise IndexError(f"No executable found in {downloaded}")
            elif len(exe_search_res) == 1:
                exe = exe_search_res.list[0]
                print(f"✅ Found exact match for '{tool_name}': {exe}")
            else:
                exe = exe_search_res.sort(lambda x: x.size("kb")).list[-1]
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
        Terminal().run(f"sudo mv {exe} {LINUX_INSTALL_PATH}/").capture().print_if_unsuccessful(desc=f"MOVING executable `{exe}` to {LINUX_INSTALL_PATH}", strict_err=True, strict_returncode=True)
    else:
        exe.move(folder=LINUX_INSTALL_PATH, overwrite=True)

    if delete:
        print("🗑️  Cleaning up temporary files...")
        downloaded.delete(sure=True)
        print("✅ Temporary files removed")

    exe_new_location = P(LINUX_INSTALL_PATH).joinpath(exe.name)
    print(f"✅ Executable installed at: {exe_new_location}\n{'='*80}")
    return exe_new_location