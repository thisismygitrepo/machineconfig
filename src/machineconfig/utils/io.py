from __future__ import annotations

from typing import Any, Union, Optional, Mapping
from pathlib import Path
import json
import pickle
import configparser


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


def read_ini(path: "Path", encoding: Optional[str] = None):
    if not Path(path).exists() or Path(path).is_dir():
        raise FileNotFoundError(f"File not found or is a directory: {path}")
    import configparser
    res = configparser.ConfigParser()
    res.read(filenames=[str(path)], encoding=encoding)
    return res


def read_json(path: "Path", r: bool = False, **kwargs: Any) -> Any:  # return could be list or dict etc
    import json
    try:
        mydict = json.loads(Path(path).read_text(encoding="utf-8"), **kwargs)
    except Exception:
        import re
        def remove_comments(text: str) -> str:
            # remove all // single-line comments
            text = re.sub(r'//.*', '', text)
            # remove all /* … */ block comments (non-greedy)
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
            return text
        mydict = json.loads(remove_comments(Path(path).read_text(encoding="utf-8")), **kwargs)
    _ = r
    return mydict


def from_pickle(path: Path) -> Any:
    import pickle

    return pickle.loads(path.read_bytes())
