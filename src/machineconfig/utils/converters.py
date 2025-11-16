
import json
import sys
from pathlib import Path
import yaml
import tomli_w
import typer

def to_toml(file_path: str):
    """
    Converts a JSON or YAML file to TOML format.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found at {path}")
        raise typer.Exit(code=1)

    try:
        with open(path, "r") as f:
            if path.suffix == ".json":
                data = json.load(f)
            elif path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
            else:
                print(f"Error: Unsupported file type: {path.suffix}")
                raise typer.Exit(code=1)
    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        raise typer.Exit(code=1)

    toml_path = path.with_suffix(".toml")
    try:
        with open(toml_path, "wb") as f:
            tomli_w.dump(data, f)
        print(f"Successfully converted {path} to {toml_path}")
    except Exception as e:
        print(f"Error writing TOML file: {e}")
        raise typer.Exit(code=1)
