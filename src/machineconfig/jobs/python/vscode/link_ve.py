"""VScode task to set interpreter"""

# import os
# import json
from pathlib import Path
import argparse
# import platform


def select_interpreter(workspace_root: str):
    print(f"""
{"=" * 150}
🔗 VSCODE VE LINKER | Linking virtual environment for VS Code
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
        ve_path = Path(f.read().strip()).expanduser()

    venv_link = Path(workspace_root).joinpath(".venv")

    if venv_link.exists() and not venv_link.is_symlink():
        print(f"""
{"⚠️" * 20}
❌ ERROR | .venv already exists and is not a symlink
📂 Path: {venv_link}
{"⚠️" * 20}
""")
        return

    venv_link.symlink_to(target=ve_path.expanduser().absolute())

    print(f"""
{"=" * 150}
✅ SUCCESS | Virtual environment linked successfully
🔗 Link: {venv_link}
🎯 Target: {ve_path.expanduser().absolute()}
{"=" * 150}
""")


def main():
    parser = argparse.ArgumentParser(description="Link ve from repo to ve location.")
    parser.add_argument("workspace_path", type=str, help="The workspace path")

    args = parser.parse_args()
    select_interpreter(args.workspace_path)


if __name__ == "__main__":
    main()
