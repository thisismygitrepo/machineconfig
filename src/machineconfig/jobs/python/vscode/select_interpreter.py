
"""VScode task to set interpreter
"""

# import os
# import json
from crocodile.file_management import P as Path, Read, Save
import argparse
import platform


def select_interpreter(workspace_root: str):
    path = Path(workspace_root).joinpath('.ve_path')
    with open(path, 'r', encoding='utf-8') as f:
        python_path = Path(f.read().strip().replace("~", str(Path.home())))

    if platform.system() == 'Windows':
        python_path = python_path.joinpath('Scripts', 'python.exe')
    elif platform.system() == 'Linux':
        python_path = python_path.joinpath('bin', 'python')
    elif platform.system() == 'Darwin':
        python_path = python_path.joinpath('bin', 'python')
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")

    # tmp = os.getenv('APPDATA')
    # assert tmp is not None
    # settings_path = Path(tmp).joinpath('Code', 'User', 'settings.json')
    work_space_settings = Path(workspace_root).joinpath('.vscode', 'settings.json').create(parents_only=True)
    if not work_space_settings.exists():
        work_space_settings.touch()
        work_space_settings.write_text("{}")
    settings = Read.json(work_space_settings)
    settings['python.defaultInterpreterPath'] = str(python_path)
    Save.json(obj=settings, path=work_space_settings, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Set Python Interpretor in VSCode settings.')
    parser.add_argument('workspace_path', type=str, help='The workspace path')

    args = parser.parse_args()
    select_interpreter(args.workspace_path)


if __name__ == "__main__":
    main()
