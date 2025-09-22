"""
Generate uv add commands from pyproject.toml dependency groups.
"""

from pathlib import Path
import tomllib
from typing import Any


def generate_uv_add_commands(pyproject_path: Path, output_path: Path) -> None:
    """
    Generate uv add commands for each dependency group in pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file
        output_path: Path where to write the uv add commands
    """
    # Read pyproject.toml
    with open(pyproject_path, "rb") as f:
        pyproject_data: dict[str, Any] = tomllib.load(f)

    commands: list[str] = []

    # Handle main dependencies (no group)
    if "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
        main_deps = pyproject_data["project"]["dependencies"]
        if main_deps:
            # Extract package names without version constraints
            package_names = [extract_package_name(dep) for dep in main_deps]
            commands.append(f"uv add {' '.join(package_names)}")

    # Handle optional dependencies as groups
    if "project" in pyproject_data and "optional-dependencies" in pyproject_data["project"]:
        optional_deps = pyproject_data["project"]["optional-dependencies"]
        for group_name, deps in optional_deps.items():
            if deps:
                package_names = [extract_package_name(dep) for dep in deps]
                commands.append(f"uv add {' '.join(package_names)} --group {group_name}")

    # Handle dependency-groups (like dev)
    if "dependency-groups" in pyproject_data:
        dep_groups = pyproject_data["dependency-groups"]
        for group_name, deps in dep_groups.items():
            if deps:
                package_names = [extract_package_name(dep) for dep in deps]
                if group_name == "dev":
                    commands.append(f"uv add {' '.join(package_names)} --dev")
                else:
                    commands.append(f"uv add {' '.join(package_names)} --group {group_name}")

    # Write commands to output file
    with open(output_path, "w") as f:
        for command in commands:
            f.write(command + "\n")

    print(f"Generated {len(commands)} uv add commands in {output_path}")


def extract_package_name(dependency_spec: str) -> str:
    """
    Extract package name from dependency specification.

    Examples:
        "rich>=14.0.0" -> "rich"
        "requests>=2.32.5" -> "requests"
        "pywin32" -> "pywin32"
        "package[extra]>=1.0" -> "package"
    """
    # Handle extras like "package[extra]>=1.0" first
    if "[" in dependency_spec:
        dependency_spec = dependency_spec.split("[")[0].strip()

    # Split on common version operators and take the first part
    for operator in [">=", "<=", "==", "!=", ">", "<", "~=", "===", "@"]:
        if operator in dependency_spec:
            return dependency_spec.split(operator)[0].strip()

    # Return as-is if no version constraint found
    return dependency_spec.strip()


if __name__ == "__main__":
    # Example usage
    current_dir = Path.cwd()
    pyproject_file = current_dir / "pyproject.toml"
    output_file = current_dir / "uv_add_commands.txt"

    if pyproject_file.exists():
        generate_uv_add_commands(pyproject_file, output_file)
    else:
        print(f"pyproject.toml not found at {pyproject_file}")
