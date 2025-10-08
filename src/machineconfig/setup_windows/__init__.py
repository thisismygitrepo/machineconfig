
from pathlib import Path

APPS = Path(__file__).parent.joinpath("apps.ps1")
UV = Path(__file__).parent.joinpath("uv.ps1")

DOCKER = Path(__file__).parent.joinpath("others/docker.ps1")
OBS = Path(__file__).parent.joinpath("others/obs.ps1")
POWER_OPTIONS = Path(__file__).parent.joinpath("others/power_options.ps1")

SSH_SERVER = Path(__file__).parent.joinpath("ssh/openssh_server.ps1")
