
from machineconfig.utils.utils import get_latest_release
import crocodile.toolbox as tb


url = "https://github.com/Significant-Gravitas/Auto-GPT"


def main(version=None):
    # _ = version
    # latest = get_latest_release(url) 
    dest = tb.P.home().joinpath("code/foreign/Auto-GPT").delete(sure=True)
    # download = tb.P(f"https://github.com/Significant-Gravitas/Auto-GPT/archive/refs/tags/{latest[-1]}.zip").download(name="Auto-GPT.zip").unzip().search()[0].move(folder=dest)
    program = """

activate_ve latest
cd ~/code/foreign
git clone -b stable https://github.com/Significant-Gravitas/Auto-GPT.git
cd Auto-GPT
pip install -r requirements.txt
cp .env.template .env

"""


if __name__ == "__main__":
    main()
