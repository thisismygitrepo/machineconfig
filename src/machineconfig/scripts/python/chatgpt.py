
"""GPT
"""

from crocodile.file_management import P
from machineconfig.utils.utils import PROGRAM_PATH
import argparse
import platform


base_dir = P.home().joinpath("dotfiles/gpt/prompts")
# https://platform.openai.com/docs/models/gpt-4


def main():
    api_key = P.home().joinpath("dotfiles/creds/tokens/openai_api.txt").read_text().lstrip().rstrip()
    parser = argparse.ArgumentParser()
    _args = parser.parse_args()

    # config = P.home().joinpath(".config/chatgpt/config.json")
    # if args.base is not None: base_txt = base_dir.joinpath(args.base)
    # else: base_txt = P.tmpfile().write_text("")

    if platform.system() == "Windows":
        cmd = f"""
$OPENAI_API_KEY = '{api_key}'
"""
    else:
        cmd = f"""
"""
    PROGRAM_PATH.write_text(cmd)


if __name__ == '__main__':
    main()
