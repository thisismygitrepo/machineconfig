
import crocodile.toolbox as tb
from crocodile.comms.gdrive import GDriveAPI

# app_name = "something"
# tb.T().run(f"cargo install {app_name}")

url = r"https://github.com/lunaryorn/mdcat"
link = tb.P(url)
res = f"""
git clone {url}
cd {url.split('/')[-1]}
cargo install --path .
mv .cargo/bin/{url.split('/')[-1]}.exe {tb.get_env().WindowsApps}/
bu_gdrive_sx res_path -zR
"""
