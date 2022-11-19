
import crocodile.toolbox as tb
from crocodile.comms.gdrive import GDriveAPI
import platform
# app_name = "something"
# tb.T().run(f"cargo install {app_name}")


def get_shell_script(url=r"https://github.com/atanunq/viu"):
    repo = url.split('/')[-1]

    exe = f".cargo/bin/{repo}"
    move_command = f"mv {exe}.exe {tb.get_env().WindowsApps.as_posix()}/" if platform.platform() == "Windows" else f"sudo mv {exe} /usr/local/bin/"

    res = f"""
    cd ~
    git clone --depth 1 {url} 
    cd {repo}
    cargo install --path .
    rm -rdf ~/{repo}
    bu_gdrive_sx {exe} -zR
    {move_command}
    """
    # tb.P(repo).delete(sure=True)
    print(res)


# after cargo install diskonaut
# then mv ~/.cargo/bin/diskonaut.exe ~/AppData/Local/Microsoft/WindowsApps/
# then bu_gdrive_sx.ps1 .\diskonaut.exe -sRz  # zipping is vital to avoid security layers and keep file metadata.
