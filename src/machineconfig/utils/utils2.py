

from pathlib import Path
from typing import Optional, Any
# import time
# from typing import Callable, Literal, TypeVar, ParamSpec


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
    return ''.join(random.choices(population, k=length))


def read_ini(path: 'Path', encoding: Optional[str] = None):
    if not Path(path).exists() or Path(path).is_dir(): raise FileNotFoundError(f"File not found or is a directory: {path}")
    import configparser
    res = configparser.ConfigParser()
    res.read(filenames=[str(path)], encoding=encoding)
    return res
def read_json(path: 'Path', r: bool = False, **kwargs: Any) -> Any:  # return could be list or dict etc
    import json
    try:
        mydict = json.loads(Path(path).read_text(encoding='utf-8'), **kwargs)
    except Exception:
        import pyjson5
        mydict = pyjson5.loads(Path(path).read_text(encoding='utf-8'), **kwargs)  # file has C-style comments.
    _ = r
    return mydict
def read_toml(path: 'Path'):
    import tomli
    return tomli.loads(path.read_text(encoding='utf-8'))

def pprint(obj: dict[Any, Any], title: str) -> None:
    from rich import inspect
    inspect(type("TempStruct", (object,), obj)(), value=False, title=title, docs=False, dunder=False, sort=False)
def get_repr(obj: dict[Any, Any], sep: str = "\n", justify: int = 15, quotes: bool = False):
    return sep.join([f"{key:>{justify}} = {repr(val) if quotes else val}" for key, val in obj.items()])


# T = TypeVar('T')
# PS = ParamSpec('PS')

# class RepeatUntilNoException:
#     """
#     Repeat function calling if it raised an exception and/or exceeded the timeout, for a maximum of `retry` times.
#     * Alternative: `https://github.com/jd/tenacity`
#     """
#     def __init__(self, retry: int, sleep: float, timeout: Optional[float] = None, scaling: Literal["linear", "exponential"] = "exponential"):
#         self.retry = retry
#         self.sleep = sleep
#         self.timeout = timeout
#         self.scaling: Literal["linear", "exponential"] = scaling
#     def __call__(self, func: Callable[PS, T]) -> Callable[PS, T]:
#         from functools import wraps
#         if self.timeout is not None:
#             import warpt_time_decorator
#             func = wrapt_timeout_decorator.timeout(self.timeout)(func)
#         @wraps(wrapped=func)
#         def wrapper(*args: PS.args, **kwargs: PS.kwargs):
#             t0 = time.time()
#             for idx in range(self.retry):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception as ex:
#                     match self.scaling:
#                         case "linear":
#                             sleep_time = self.sleep * (idx + 1)
#                         case "exponential":
#                             sleep_time = self.sleep * (idx + 1)**2
#                     print(f"""💥 [RETRY] Function {func.__name__} call failed with error:
# {ex}
# Retry count: {idx}/{self.retry}. Sleeping for {sleep_time} seconds.
# Total elapsed time: {time.time() - t0:0.1f} seconds.""")
#                     print(f"""💥 Robust call of `{func}` failed with ```{ex}```.\nretrying {idx}/{self.retry} more times after sleeping for {sleep_time} seconds.\nTotal wait time so far {time.time() - t0: 0.1f} seconds.""")
#                     time.sleep(sleep_time)
#             raise RuntimeError(f"💥 Robust call failed after {self.retry} retries and total wait time of {time.time() - t0: 0.1f} seconds.\n{func=}\n{args=}\n{kwargs=}")
#         return wrapper
