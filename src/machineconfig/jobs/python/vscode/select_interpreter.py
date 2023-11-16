
import os
import json
from pathlib import Path
import argparse


def select_interpreter(workspace_root: str):
    path = Path(workspace_root).joinpath('.ve_path')
    with open(path, 'r') as f:
        python_path = Path(f.read().strip().replace("~", str(Path.home())))

    settings_path = os.path.join(os.getenv('APPDATA'), 'Code', 'User', 'settings.json')

    with open(settings_path, 'r+') as f:
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
