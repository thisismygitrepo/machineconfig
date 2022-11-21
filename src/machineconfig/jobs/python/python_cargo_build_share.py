
import crocodile.toolbox as tb
from crocodile.comms.gdrive import GDriveAPI
import platform
# app_name = "something"
# tb.T().run(f"cargo install {app_name}")


def get_shell_script(url=r"https://github.com/atanunq/viu"):
    tool_name = url.split('/')[-1]

    exe = f".cargo/bin/{tool_name}" + (".exe" if platform.system() == "Windows" else "")

    # move command is not required since tool will go to .cargo/bin which is in PATH by default.
    # move_command = f"mv {exe} {tb.get_env().WindowsApps.as_posix()}/" if platform.platform() == "Windows" else f"sudo mv {exe} /usr/local/bin/"
    # {move_command}

    script = f"""
    cd ~
    git clone --depth 1 {url} 
    cd {tool_name}
    cargo install --path .
    bu_gdrive_sx {exe} -zR
    """
    print(f"Executing {script}")
    tb.Terminal().run(script, shell="pwsh")
    tb.P.home().joinpath(tool_name).delete(sure=True)


# after cargo install diskonaut
# then mv ~/.cargo/bin/diskonaut.exe ~/AppData/Local/Microsoft/WindowsApps/
# then bu_gdrive_sx.ps1 .\diskonaut.exe -sRz  # zipping is vital to avoid security layers and keep file metadata.
