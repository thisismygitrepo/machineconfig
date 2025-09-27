
from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.utils.source_of_truth import WINDOWS_INSTALL_PATH, LINUX_INSTALL_PATH, INSTALL_VERSION_ROOT

from pathlib import Path
from typing import Any, Optional
import subprocess
import platform


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


def check_tool_exists(tool_name: str) -> bool:
    if platform.system() == "Windows":
        tool_name = tool_name.replace(".exe", "") + ".exe"
        res1 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name).is_file()])
        tool_name = tool_name.replace(".exe", "") + ".exe"
        res2 = any([Path(WINDOWS_INSTALL_PATH).joinpath(tool_name).is_file(), Path.home().joinpath("AppData/Roaming/npm").joinpath(tool_name).is_file()])
        return res1 or res2
    elif platform.system() in ["Linux", "Darwin"]:
        root_path = Path(LINUX_INSTALL_PATH)
        return any([Path("/usr/local/bin").joinpath(tool_name).is_file(), Path("/usr/bin").joinpath(tool_name).is_file(), root_path.joinpath(tool_name).is_file()])
    else:
        raise NotImplementedError(f"platform {platform.system()} not implemented")


def check_if_installed_already(exe_name: str, version: Optional[str], use_cache: bool) -> tuple[str, str, str]:
    print(f"\n{'=' * 80}\n🔍 CHECKING INSTALLATION STATUS: {exe_name} 🔍\n{'=' * 80}")
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


def parse_apps_installer_linux(txt: str) -> dict[str, Any]:
    """Parse Linux shell installation scripts into logical chunks.
    
    Supports two formats:
    1. Legacy format with 'yes '' | sed 3q; echo "----------------------------- installing' delimiter
    2. New format with # --BLOCK:<name>-- comment signatures
    
    Returns:
        dict[str, str]: Dictionary mapping block/section names to their installation scripts
    """
    # Try new block format first
    if "# --BLOCK:" in txt:
        import re
        # Split by block signatures: # --BLOCK:<name>--
        blocks = re.split(r'# --BLOCK:([^-]+)--', txt)
        res: dict[str, str] = {}
        
        # Process blocks in pairs (block_name, block_content)
        for i in range(1, len(blocks), 2):
            if i + 1 < len(blocks):
                block_name = blocks[i].strip()
                block_content = blocks[i + 1].strip()
                if block_content:
                    res[block_name] = block_content
        
        return res
    
    # Legacy format fallback
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
