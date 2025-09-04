from machineconfig.utils.utils import PROGRAM_PATH
from pathlib import Path
import platform

def main():
    print("\n" + "=" * 50)
    print("🚀 Welcome to the Windows Network Drive Mounting Wizard")
    print("=" * 50 + "\n")

    drive_location = input("🔗 Enter the network drive location (e.g., //192.168.1.100/Share): ")
    machine_name = drive_location.split("//")[1].split("/")[0]

    mount_point_input = input(f"📂 Enter the mount point directory (e.g., /mnt/network) [Default: ~/data/mount_nw/{machine_name}]: ")
    if mount_point_input == "":
        mount_point = Path.home().joinpath(fr"data/mount_nw/{machine_name}")
    else:
        mount_point = Path(mount_point_input).expanduser()

    print(f"\n🌐 Network Drive Location: {drive_location}")
    print(f"📁 Mount Point: {mount_point}\n")

    username = input("👤 Enter the username: ")
    password = input("🔒 Enter the password: ")

    if platform.system() in ["Linux", "Darwin"]:
        print("\n🔧 Saving configuration for Linux...")
        PROGRAM_PATH.write_text(f"""
drive_location='{drive_location}'
mount_point='{mount_point}'
username='{username}'
password='{password}'

""", encoding="utf-8")
        print("✅ Configuration saved successfully!\n")

    elif platform.system() == "Windows":
        print("❌ Windows platform is not yet supported.")
        raise NotImplementedError

    print("🎉 Windows Network Drive Mounting Process Completed!\n")

if __name__ == '__main__':
    main()
