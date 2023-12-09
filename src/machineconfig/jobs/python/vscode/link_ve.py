
"""VScode task to set interpreter
"""

# import os
# import json
from crocodile.file_management import P as Path  # , Read, Save
import argparse
# import platform


def select_interpreter(workspace_root: str):
    path = Path(workspace_root).joinpath('.ve_path')
    with open(path, 'r', encoding='utf-8') as f:
        ve_path = Path(f.read().strip().replace("~", str(Path.home())))
    Path(workspace_root).joinpath(".venv").symlink_to(ve_path.expanduser().absolute())


def main():
    parser = argparse.ArgumentParser(description='Link ve from repo to ve location.')
    parser.add_argument('workspace_path', type=str, help='The workspace path')

    args = parser.parse_args()
    select_interpreter(args.workspace_path)


if __name__ == "__main__":
    main()
