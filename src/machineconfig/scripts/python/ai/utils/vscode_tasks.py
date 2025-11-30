import json
from pathlib import Path
from typing import Any


def add_lint_and_type_check_task(repo_root: Path) -> None:
    vscode_dir = repo_root / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    tasks_json_path = vscode_dir / "tasks.json"

    task_to_add = {
        "label": "lint_and_type_check",
        "type": "shell",
        "linux": {"command": "bash", "args": ["./.ai/scripts/lint_and_type_check.sh"]},
        "osx": {"command": "bash", "args": ["./.ai/scripts/lint_and_type_check.sh"]},
        "windows": {"command": "pwsh", "args": ["-File", "./.ai/scripts/lint_and_type_check.ps1"]},
        "presentation": {"reveal": "always", "panel": "new"},
        "problemMatcher": [],
    }

    if tasks_json_path.exists():
        json_data = tasks_json_path.read_text(encoding="utf-8")
        if not json_data.strip():
            tasks_config: dict[str, Any] = {"version": "2.0.0", "tasks": []}
        else:
            tasks_config = json.loads(json_data)
            assert isinstance(tasks_config, dict)
        if "tasks" not in tasks_config:
            tasks_config["tasks"] = []
        
        # Remove any existing entries with the same label to prevent duplicates
        tasks_config["tasks"] = [
            t for t in tasks_config["tasks"] if t.get("label") != task_to_add["label"]
        ]
        tasks_config["tasks"].append(task_to_add)
    else:
        tasks_config = {"version": "2.0.0", "tasks": [task_to_add]}

    with tasks_json_path.open("w") as f:
        json.dump(tasks_config, f, indent="\t")
