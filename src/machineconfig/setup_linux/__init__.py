
from pathlib import Path

APPS = Path(__file__).parent.joinpath("apps.sh")
UV = Path(__file__).parent.joinpath("uv.sh")

APPS_DESKTOP = Path(__file__).parent.joinpath("apps_desktop.sh")
APPS_GUI = Path(__file__).parent.joinpath("apps_gui.sh")

SSH_SERVER = Path(__file__).parent.joinpath("ssh/openssh_server.sh")
