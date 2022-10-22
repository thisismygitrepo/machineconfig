
import crocodile.toolbox as tb
from crocodile.comms.gdrive import GDriveAPI

# app_name = "something"
# tb.T().run(f"cargo install {app_name}")

def get_shell_script(url=r"https://github.com/atanunq/viu"):
    repo = url.split('/')[-1]
    exe = f".cargo/bin/{repo}.exe"
    res = f"""
    cd ~
    git clone {url}
    cd {repo}
    cargo install --path .
    bu_gdrive_sx {exe} -zR
    mv {exe} {tb.get_env().WindowsApps.as_posix()}/
    """
    # tb.P(repo).delete(sure=True)
    print(res)


# after cargo install diskonaut
# then mv ~/.cargo/bin/diskonaut.exe ~/AppData/Local/Microsoft/WindowsApps/
# then bu_gdrive_sx.ps1 .\diskonaut.exe -sRz  # zipping is vital to avoid security layers and keep file metadata.

