
import crocodile.toolbox as tb
from crocodile.comms.gdrive import GDriveAPI

app_name = "something"
tb.T().run(f"cargo install {app_name}")
exe = tb.P.home().joinpath(f".cargo/bin/{app_name}.exe")
res_path = exe.move(folder=tb.get_env().WindowsApps)
GDriveAPI().upload_and_share(local_path=res_path, zip_first=True)
