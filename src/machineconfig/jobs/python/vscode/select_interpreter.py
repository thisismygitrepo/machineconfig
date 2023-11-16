
"""VScode task to set interpreter
"""

import os
import json
from pathlib import Path
import argparse


def select_interpreter(workspace_root: str):
    path = Path(workspace_root).joinpath('.ve_path')
    with open(path, 'r', encoding='utf-8') as f:
        python_path = Path(f.read().strip().replace("~", str(Path.home())))

    tmp = os.getenv('APPDATA')
    assert tmp is not None
    settings_path = Path(tmp).joinpath('Code', 'User', 'settings.json')

    with open(settings_path, 'r+', encoding='utf-8') as f:
        settings = json.load(f)
        settings['python.pythonPath'] = python_path
        f.seek(0)
        json.dump(settings, f, indent=4)
        f.truncate()


def main():
    parser = argparse.ArgumentParser(description='Select Python interpreter.')
    parser.add_argument('workspace_path', type=str, help='The workspace path')

    args = parser.parse_args()
    select_interpreter(args.workspace_path)


if __name__ == "__main__":
    main()
