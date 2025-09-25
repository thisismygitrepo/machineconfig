from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path
import tomllib


def _get_version() -> str:
    name: str = "machineconfig"
    try:
        return _pkg_version(name)
    except PackageNotFoundError:
        pass

    root: Path = Path(__file__).resolve().parents[2]
    pyproject: Path = root / "pyproject.toml"
    if pyproject.is_file():
        with pyproject.open("rb") as f:
            data: dict[str, object] = tomllib.load(f)
        project = data.get("project")
        if isinstance(project, dict):
            version = project.get("version")
            if isinstance(version, str) and version:
                return version
    return "0.0.0"


__version__: str = _get_version()
__all__: list[str] = ["__version__"]
