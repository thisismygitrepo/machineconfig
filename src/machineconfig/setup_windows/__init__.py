
from pathlib import Path

UV = Path(__file__).parent.joinpath("uv.ps1")

SSH_SERVER =  Path(__file__).parent.joinpath("ssh/openssh-server.ps1")
SSH_ADD_KEY = Path(__file__).parent.joinpath("ssh/add-ssh-key.ps1")

INTERACTIVE = Path(__file__).parent.joinpath("web_shortcuts/interactive.ps1")
LIVE =        Path(__file__).parent.joinpath("web_shortcuts/live_from_github.ps1")

