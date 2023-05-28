
from crocodile.file_management import Path as P
from machineconfig.utils.utils import PROGRAM_PATH
import argparse

base_dir = P.home().joinpath("dotfiles/gpt/prompts")


def main():
    api_key = P.home().joinpath("dotfiles/creds/tokens/openai_api.txt").read_text().lstrip().rstrip()
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", "-b", default=None, type=str)
    args = parser.parse_args()
    if args.base is not None:
        base_txt = base_dir.joinpath(args.base)
        print(base_txt)
        cmd = f"""
$base = $(cat {base_txt})
chatgpt --base_prompt $base
    """
    else:
        cmd = f"""
"""
    PROGRAM_PATH.write_text(cmd)


if __name__ == '__main__':
    main()
