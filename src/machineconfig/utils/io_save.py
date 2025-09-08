from __future__ import annotations

from typing import Any, Union, Optional, Mapping
from pathlib import Path
import json
import pickle
import configparser
import toml
import yaml


PathLike = Union[str, Path]


def _ensure_parent(path: PathLike) -> Path:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    return path_obj


def save_pickle(obj: Any, path: PathLike, verbose: bool = False) -> Path:
    path_obj = _ensure_parent(path)
    with open(path_obj, "wb") as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)
    if verbose:
        print(f"Saved pickle -> {path_obj}")
    return Path(path_obj)


def save_json(obj: Any, path: PathLike, indent: Optional[int] = None, verbose: bool = False) -> Path:
    path_obj = _ensure_parent(path)
    with open(path_obj, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")
    if verbose:
        print(f"Saved json -> {path_obj}")
    return Path(path_obj)


def save_toml(obj: Mapping[str, Any], path: PathLike, verbose: bool = False) -> Path:
    path_obj = _ensure_parent(path)
    with open(path_obj, "w", encoding="utf-8") as fh:
        toml.dump(obj, fh)
    if verbose:
        print(f"Saved toml -> {path_obj}")
    return Path(path_obj)


def save_yaml(obj: Any, path: PathLike, verbose: bool = False) -> Path:
    path_obj = _ensure_parent(path)
    with open(path_obj, "w", encoding="utf-8") as fh:
        yaml.safe_dump(obj, fh, sort_keys=False)
    if verbose:
        print(f"Saved yaml -> {path_obj}")
    return Path(path_obj)


def save_ini(path: PathLike, obj: Mapping[str, Mapping[str, Any]], verbose: bool = False) -> Path:
    cp = configparser.ConfigParser()
    for section, values in obj.items():
        cp[section] = {str(k): str(v) for k, v in values.items()}
    path_obj = _ensure_parent(path)
    with open(path_obj, "w", encoding="utf-8") as fh:
        cp.write(fh)
    if verbose:
        print(f"Saved ini -> {path_obj}")
    return Path(path_obj)


class Save:
    """

    Provides static methods for common serialization formats while ensuring
    parent directories exist and returning a `P` path object.
    """

    @staticmethod
    def pickle(obj: Any, path: PathLike, verbose: bool = False, **_kwargs: Any) -> Path:
        return save_pickle(obj=obj, path=path, verbose=verbose)

    @staticmethod
    def json(obj: Any, path: PathLike, indent: Optional[int] = None, verbose: bool = False, **_kwargs: Any) -> Path:
        return save_json(obj=obj, path=path, indent=indent, verbose=verbose)

    @staticmethod
    def toml(obj: Mapping[str, Any], path: PathLike, verbose: bool = False, **_kwargs: Any) -> Path:
        return save_toml(obj=obj, path=path, verbose=verbose)

    @staticmethod
    def yaml(obj: Any, path: PathLike, verbose: bool = False, **_kwargs: Any) -> Path:
        return save_yaml(obj=obj, path=path, verbose=verbose)

    @staticmethod
    def ini(obj: Mapping[str, Mapping[str, Any]], path: PathLike, verbose: bool = False, **_kwargs: Any) -> Path:
        return save_ini(path=path, obj=obj, verbose=verbose)
