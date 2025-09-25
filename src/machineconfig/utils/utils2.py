from pathlib import Path
from typing import Optional, Any


def randstr(length: int = 10, lower: bool = True, upper: bool = True, digits: bool = True, punctuation: bool = False, safe: bool = False, noun: bool = False) -> str:
    if safe:
        import secrets

        return secrets.token_urlsafe(length)  # interannly, it uses: random.SystemRandom or os.urandom which is hardware-based, not pseudo
    if noun:
        import randomname

        return randomname.get_name()
    import string
    import random

    population = (string.ascii_lowercase if lower else "") + (string.ascii_uppercase if upper else "") + (string.digits if digits else "") + (string.punctuation if punctuation else "")
    return "".join(random.choices(population, k=length))


def split[T](iterable: list[T], every: int = 1, to: Optional[int] = None) -> list[list[T]]:
    import math

    every = every if to is None else math.ceil(len(iterable) / to)
    res: list[list[T]] = []
    for ix in range(0, len(iterable), every):
        if ix + every < len(iterable):
            tmp = iterable[ix : ix + every]
        else:
            tmp = iterable[ix : len(iterable)]
        res.append(list(tmp))
    return list(res)


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
        import pyjson5
        mydict = pyjson5.loads(Path(path).read_text(encoding="utf-8"), **kwargs)  # file has C-style comments.
    _ = r
    return mydict


def read_toml(path: "Path"):
    import tomli

    return tomli.loads(path.read_text(encoding="utf-8"))


def pprint(obj: dict[Any, Any], title: str) -> None:
    from rich import inspect

    inspect(type("TempStruct", (object,), obj)(), value=False, title=title, docs=False, dunder=False, sort=False)


def get_repr(obj: dict[Any, Any], sep: str = "\n", justify: int = 15, quotes: bool = False):
    return sep.join([f"{key:>{justify}} = {repr(val) if quotes else val}" for key, val in obj.items()])


def human_friendly_dict(d: dict[str, Any]) -> dict[str, Any]:
    from datetime import datetime

    result = {}
    for k, v in d.items():
        if isinstance(v, float):
            result[k] = f"{v:.2f}"
        elif isinstance(v, bool):
            result[k] = "✓" if v else "✗"
        elif isinstance(v, int) and len(str(v)) == 13 and v > 0:  # assuming ms timestamp
            dt = datetime.fromtimestamp(v / 1000)
            result[k] = dt.strftime("%Y-%m-%d %H:%M")
        else:
            result[k] = v
    return result
