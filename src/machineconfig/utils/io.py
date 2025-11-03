
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


def pwd2key(password: str, salt: Optional[bytes] = None, iterations: int = 10) -> bytes:  # Derive a secret key from a given password and salt"""
    import base64
    if salt is None:
        import hashlib
        m = hashlib.sha256()
        m.update(password.encode(encoding="utf-8"))
        return base64.urlsafe_b64encode(s=m.digest())  # make url-safe bytes required by Ferent.
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    return base64.urlsafe_b64encode(PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations, backend=None).derive(password.encode()))


def encrypt(msg: bytes, key: Optional[bytes] = None, pwd: Optional[str] = None, salted: bool = True, iteration: Optional[int] = None, gen_key: bool = False) -> bytes:
    import base64
    from cryptography.fernet import Fernet

    salt, iteration = None, None
    if pwd is not None:  # generate it from password
        assert (key is None) and (type(pwd) is str), "❌ You can either pass key or pwd, or none of them, but not both."
        import secrets
        iteration = iteration or secrets.randbelow(exclusive_upper_bound=1_000_000)
        salt = secrets.token_bytes(nbytes=16) if salted else None
        key_resolved = pwd2key(password=pwd, salt=salt, iterations=iteration)
    elif key is None:
        if gen_key:
            key_resolved = Fernet.generate_key()
            Path.home().joinpath("dotfiles/creds/data/encrypted_files_key.bytes").write_bytes(key_resolved)
        else:
            try:
                key_resolved = Path.home().joinpath("dotfiles/creds/data/encrypted_files_key.bytes").read_bytes()
                print(f"⚠️ Using key from: {Path.home().joinpath('dotfiles/creds/data/encrypted_files_key.bytes')}")
            except FileNotFoundError as err:
                print("\n" * 3, "~" * 50, """Consider Loading up your dotfiles or pass `gen_key=True` to make and save one.""", "~" * 50, "\n" * 3)
                raise FileNotFoundError(err) from err
    elif isinstance(key, (str, Path)):
        key_resolved = Path(key).read_bytes()  # a path to a key file was passed, read it:
    elif type(key) is bytes:
        key_resolved = key  # key passed explicitly
    else:
        raise TypeError("❌ Key must be either a path, bytes object or None.")
    code = Fernet(key=key_resolved).encrypt(msg)
    if pwd is not None and salt is not None and iteration is not None:
        return base64.urlsafe_b64encode(b"%b%b%b" % (salt, iteration.to_bytes(4, "big"), base64.urlsafe_b64decode(code)))
    return code


def decrypt(token: bytes, key: Optional[bytes] = None, pwd: Optional[str] = None, salted: bool = True) -> bytes:
    import base64
    if pwd is not None:
        assert key is None, "❌ You can either pass key or pwd, or none of them, but not both."
        if salted:
            decoded = base64.urlsafe_b64decode(token)
            salt, iterations, token = decoded[:16], decoded[16:20], base64.urlsafe_b64encode(decoded[20:])
            key_resolved = pwd2key(password=pwd, salt=salt, iterations=int.from_bytes(bytes=iterations, byteorder="big"))
        else:
            key_resolved = pwd2key(password=pwd)  # trailing `;` prevents IPython from caching the result.
    elif type(key) is bytes:
        assert pwd is None, "❌ You can either pass key or pwd, or none of them, but not both."
        key_resolved = key  # passsed explicitly
    elif key is None:
        key_resolved = Path.home().joinpath("dotfiles/creds/data/encrypted_files_key.bytes").read_bytes()  # read from file
    elif isinstance(key, (str, Path)):
        key_resolved = Path(key).read_bytes()  # passed a path to a file containing kwy
    else:
        raise TypeError(f"❌ Key must be either str, P, Path, bytes or None. Recieved: {type(key)}")
    from cryptography.fernet import Fernet
    return Fernet(key=key_resolved).decrypt(token)
