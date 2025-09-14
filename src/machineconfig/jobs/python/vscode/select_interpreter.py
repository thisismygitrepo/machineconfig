"""VScode task to set interpreter"""

# import os
# import json
from pathlib import Path
from machineconfig.utils.io_save import save_json
from machineconfig.utils.utils2 import read_json
import argparse
import platform


def select_interpreter(workspace_root: str):
    print(f"""
{"=" * 150}
🐍 PYTHON INTERPRETER | Setting up VS Code Python interpreter
📂 Workspace: {workspace_root}
{"=" * 150}
""")

    path = Path(workspace_root).joinpath(".ve_path")
    if not path.exists():
        print(f"""
{"⚠️" * 20}
❌ ERROR | Could not find .ve_path file in workspace
📂 Expected at: {path}
{"⚠️" * 20}
""")
        return

    with open(path, "r", encoding="utf-8") as f:
        python_path = Path(f.read().strip()).expanduser()

    print(f"📁 Virtual environment path: {python_path}")

    if platform.system() == "Windows":
        python_path = python_path.joinpath("Scripts", "python.exe")
    elif platform.system() == "Linux":
        python_path = python_path.joinpath("bin", "python")
    elif platform.system() == "Darwin":
        python_path = python_path.joinpath("bin", "python")
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"🔍 Python interpreter path: {python_path}")

    # tmp = os.getenv('APPDATA')
    # assert tmp is not None
    # settings_path = Path(tmp).joinpath('Code', 'User', 'settings.json')
    work_space_settings = Path(workspace_root).joinpath(".vscode", "settings.json")
    work_space_settings.parent.mkdir(parents=True, exist_ok=True)
    if not work_space_settings.exists():
        print(f"📄 Creating new settings file: {work_space_settings}")
        work_space_settings.parent.mkdir(parents=True, exist_ok=True)
        work_space_settings.touch()
        work_space_settings.write_text("{}", encoding="utf-8")
    else:
        print(f"📄 Updating existing settings file: {work_space_settings}")

    settings = read_json(work_space_settings)
    settings["python.defaultInterpreterPath"] = str(python_path)
    save_json(obj=settings, path=str(work_space_settings), indent=4)

    print(f"""
{"=" * 150}
✅ SUCCESS | Python interpreter configured successfully
🐍 Interpreter: {python_path}
📄 Settings: {work_space_settings}
{"=" * 150}
""")


def main():
    parser = argparse.ArgumentParser(description="Set Python Interpretor in VSCode settings.")
    parser.add_argument("workspace_path", type=str, help="The workspace path")

    args = parser.parse_args()
    select_interpreter(args.workspace_path)


if __name__ == "__main__":
    main()
