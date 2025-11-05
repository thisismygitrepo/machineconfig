from typing import Optional, Any

from datetime import datetime, timezone, timedelta


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


def split_timeframe(start_dt: str, end_dt: str, resolution_ms: int, to: Optional[int]=None, every_ms: Optional[int]=None) -> list[tuple[datetime, datetime]]:
    if (to is None) == (every_ms is None):
        raise ValueError("Exactly one of 'to' or 'every_ms' must be provided, not both or neither")    
    start_dt_obj = datetime.fromisoformat(start_dt).replace(tzinfo=timezone.utc)
    end_dt_obj = datetime.fromisoformat(end_dt).replace(tzinfo=timezone.utc)
    delta = end_dt_obj - start_dt_obj
    resolution = timedelta(milliseconds=resolution_ms)
    res: list[tuple[datetime, datetime]] = []    
    if to is not None:
        split_size_seconds: float = delta.total_seconds() / to
        split_size_rounded: float = round(split_size_seconds / 60) * 60
        split_size = timedelta(seconds=split_size_rounded)
        
        for idx in range(to):
            start = start_dt_obj + split_size * idx
            assert start < end_dt_obj
            if idx == to - 1:
                end = end_dt_obj
            else:
                end = start_dt_obj + split_size * (idx + 1) - resolution
            res.append((start, end))
    else:
        if every_ms is None:
            raise ValueError("every_ms cannot be None when to is None")
        split_size = timedelta(milliseconds=every_ms)
        current_start = start_dt_obj
        while current_start < end_dt_obj:
            current_end = min(current_start + split_size - resolution, end_dt_obj)
            res.append((current_start, current_end))
            current_start += split_size
    return res
def split_list[T](sequence: list[T], every: Optional[int]=None, to: Optional[int]=None) -> list[list[T]]:
    if (every is None) == (to is None):
        raise ValueError("Exactly one of 'every' or 'to' must be provided, not both or neither")
    if len(sequence) == 0:
        return []
    import math
    if to is not None:
        every = math.ceil(len(sequence) / to)
    assert every is not None
    res: list[list[T]] = []
    for ix in range(0, len(sequence), every):
        if ix + every < len(sequence):
            tmp = sequence[ix : ix + every]
        else:
            tmp = sequence[ix : len(sequence)]
        res.append(list(tmp))
    return list(res)


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


def get_repo_root(path: "Path") -> Optional["Path"]:
    from git import Repo, InvalidGitRepositoryError
    try:
        repo = Repo(path, search_parent_directories=True)
        root = repo.working_tree_dir
        if root is not None:
            from pathlib import Path
            return Path(root)
    except InvalidGitRepositoryError:
        pass
    return None


if __name__ == "__main__":
    from pathlib import Path
