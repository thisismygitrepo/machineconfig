
"""

Generate uv add commands from pyproject.toml dependency groups.

#!/bin/bash
# rm ./pyproject.toml
rm ./uv.lock
rm -rfd .venv
uv venv --python 3.13
uv init

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
    with open(pyproject_path, "rb") as f:
        pyproject_data: dict[str, Any] = tomllib.load(f)

    commands: list[str] = []

    if "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
        main_deps: list[str] = pyproject_data["project"]["dependencies"]
        if main_deps:
            package_names: list[str] = [extract_package_name(dep) for dep in main_deps]
            commands.append(f"uv add --no-cache {' '.join(package_names)}")

    if "project" in pyproject_data and "optional-dependencies" in pyproject_data["project"]:
        optional_deps: dict[str, list[str]] = pyproject_data["project"]["optional-dependencies"]
        for group_name, deps in optional_deps.items():
            if deps:
                package_names = [extract_package_name(dep) for dep in deps]
                commands.append(f"uv add --no-cache --group {group_name} {' '.join(package_names)}")

    if "dependency-groups" in pyproject_data:
        dep_groups: dict[str, list[str]] = pyproject_data["dependency-groups"]
        for group_name, deps in dep_groups.items():
            if deps:
                package_names = [extract_package_name(dep) for dep in deps]
                if group_name == "dev":
                    commands.append(f"uv add --no-cache --dev {' '.join(package_names)}")
                else:
                    commands.append(f"uv add --no-cache --group {group_name} {' '.join(package_names)}")

    # with open(output_path, "w") as f:
    #     f.write("#!/bin/bash\n")
    #     f.write("set -e\n\n")
    #     f.write("uv cache clean --force\n\n")
    #     for command in commands:
    #         f.write(command + "\n")
    script = f"""
#!/bin/bash
set -e
uv cache clean --force
rm -rfd .venv
{"".join(f"{command}\n" for command in commands)}
"""
    output_path.write_text(script.strip() + "\n", encoding="utf-8")
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


def upgrade_machine_config_version() -> None:
    """
    Upgrade machineconfig version in pyproject.toml and all source files.
    
    Reads current version from pyproject.toml, bumps it by 0.01, and replaces
    all occurrences of machineconfig>={old_version} and machineconfig[group]>={old_version}
    with the new version in Python (.py), shell (.sh), and PowerShell (.ps1) files.
    """
    current_dir: Path = Path.cwd()
    pyproject_file: Path = current_dir / "pyproject.toml"
    
    # Read current version from pyproject.toml
    with open(pyproject_file, "rb") as f:
        pyproject_data: dict[str, Any] = tomllib.load(f)
    
    current_version_str: str = pyproject_data["project"]["version"]
    version_parts: list[str] = current_version_str.split(".")
    major: int = int(version_parts[0])
    minor: int = int(version_parts[1])
    
    # Bump minor version by 1, preserving zero-padding
    new_minor: int = minor + 1
    # Preserve the same number of digits as the original minor version
    minor_width: int = len(version_parts[1])
    new_version: str = f"{major}.{new_minor:0{minor_width}d}"
    
    # Collect all optional dependency groups
    optional_groups: set[str] = set()
    if "project" in pyproject_data and "optional-dependencies" in pyproject_data["project"]:
        optional_groups.update(pyproject_data["project"]["optional-dependencies"].keys())
    if "dependency-groups" in pyproject_data:
        optional_groups.update(pyproject_data["dependency-groups"].keys())
    
    print(f"Upgrading from {current_version_str} to {new_version}")
    print(f"Found optional groups: {', '.join(sorted(optional_groups))}")
    
    # Update pyproject.toml
    content: str = pyproject_file.read_text(encoding="utf-8")
    updated_content: str = content.replace(f'version = "{current_version_str}"', f'version = "{new_version}"')
    pyproject_file.write_text(updated_content, encoding="utf-8")
    print(f"Updated pyproject.toml: {current_version_str} -> {new_version}")
    
    # Find all Python files and replace version constraints
    py_files: list[Path] = list(current_dir.glob("**/*.py")) + list(current_dir.glob("**/*.sh")) + list(current_dir.glob("**/*.ps1"))
    
    # Also include Dockerfile files
    dockerfile_files: list[Path] = [f for f in current_dir.glob("**/Dockerfile*") if f.is_file()]
    py_files.extend(dockerfile_files)
    
    files_updated: int = 0
    for file_path in py_files:
        try:
            file_content: str = file_path.read_text(encoding="utf-8")
            updated_file_content: str = file_content
            
            # Replace base constraint (without group)
            old_constraint: str = f"machineconfig>={current_version_str}"
            new_constraint: str = f"machineconfig>={new_version}"
            if old_constraint in updated_file_content:
                updated_file_content = updated_file_content.replace(old_constraint, new_constraint)
            
            # Replace constraints with optional groups
            for group in optional_groups:
                old_group_constraint: str = f"machineconfig[{group}]>={current_version_str}"
                new_group_constraint: str = f"machineconfig[{group}]>={new_version}"
                if old_group_constraint in updated_file_content:
                    updated_file_content = updated_file_content.replace(old_group_constraint, new_group_constraint)
            
            if updated_file_content != file_content:
                file_path.write_text(updated_file_content, encoding="utf-8")
                files_updated += 1
                print(f"Updated {file_path.relative_to(current_dir)}")
        except (UnicodeDecodeError, PermissionError):
            # Skip files that can't be read as text
            pass
    print(f"Updated {files_updated} files with version constraint")
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(f"cd {current_dir}; uv sync")


if __name__ == "__main__":
    upgrade_machine_config_version()
