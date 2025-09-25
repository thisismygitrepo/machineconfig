"""NFS mounting script"""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.ssh import SSH
from machineconfig.utils.terminal import Terminal
from machineconfig.utils.options import display_options, choose_ssh_host

import platform


def main():
    print("\n" + "=" * 50)
    print("🚀 Starting NFS Mounting Process")
    print("=" * 50 + "\n")

    share_info = input("🔗 Enter share path (e.g., machine:~/data/share_nfs) [Press Enter for interactive choice]: ")
    if share_info == "":
        print("\n🔍 Interactive mode selected for choosing share path.")
        tmp = choose_ssh_host(multi=False)
        assert isinstance(tmp, str)
        ssh = SSH(tmp)
        default = f"{ssh.hostname}:{ssh.run('echo $HOME').op}/data/share_nfs"
        share_info = display_options("📂 Choose a share path:", options=[f"{ssh.hostname}:{item.split(' ')[0]}" for item in ssh.run("cat /etc/exports").op.split("\n") if not item.startswith("#")] + [default], default=default)
        assert isinstance(share_info, str), f"❌ share_info must be a string. Got {type(share_info)}"

    remote_server = share_info.split(":")[0]
    share_path = share_info.split(":")[1]

    print(f"\n🌐 Remote Server: {remote_server}")
    print(f"📁 Share Path: {share_path}\n")

    if platform.system() in ["Linux", "Darwin"]:
        mount_path_1 = PathExtended(share_path)
        mount_path_2 = PathExtended.home().joinpath(f"data/mount_nfs/{remote_server}")
        if str(mount_path_1).startswith("/home"):
            mount_path_3 = PathExtended.home().joinpath(*mount_path_1.parts[3:])
        else:
            mount_path_3 = mount_path_2

        print("🔧 Preparing mount paths...")
        local_mount_point = display_options(msg="📂 Choose mount path OR input custom one:", options=[mount_path_1, mount_path_2, mount_path_3], default=mount_path_2, custom_input=True)
        assert isinstance(local_mount_point, PathExtended), f"❌ local_mount_point must be a pathlib.Path. Got {type(local_mount_point)}"
        local_mount_point = PathExtended(local_mount_point).expanduser()

        txt = f"""
share_info={share_info}
remote_server={remote_server}
share_path={share_path}
local_mount_point={local_mount_point}
        """
        # PROGRAM_PATH.write_text(txt)
        import subprocess

        subprocess.run(txt, shell=True, check=True)

        print("✅ Mount paths prepared successfully!\n")

    elif platform.system() == "Windows":
        print("\n🔍 Checking existing drives...")
        print(Terminal().run("Get-PSDrive -PSProvider 'FileSystem'", shell="powershell").op)
        driver_letter = input(r"🖥️ Choose driver letter (e.g., Z:\\) [Avoid already used ones]: ") or "Z:\\"
        txt = f"""
$server = "{remote_server}"
$sharePath = "{share_path}"
$driveLetter = "{driver_letter}"
"""
        # PROGRAM_PATH.write_text(txt)
        import subprocess

        subprocess.run(txt, shell=True, check=True)
        print("✅ Drive letter selected and configuration saved!\n")

    print("\n📄 Configuration File Content:")
    print("-" * 50)
    # print(PROGRAM_PATH.read_text(encoding="utf-8"))
    print("-" * 50 + "\n")

    print("🎉 NFS Mounting Process Completed Successfully!\n")


if __name__ == "__main__":
    main()
