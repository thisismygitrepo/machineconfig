
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


if __name__ == "__main__":
    current_dir: Path = Path.cwd()
    pyproject_file: Path = current_dir / "pyproject.toml"
    output_file: Path = current_dir / "pyproject_init.sh"
    if pyproject_file.exists():
        generate_uv_add_commands(pyproject_file, output_file)
        output_file.chmod(0o755)
        print(f"Script is executable and ready to run: {output_file}")
    else:
        print(f"pyproject.toml not found at {pyproject_file}")
