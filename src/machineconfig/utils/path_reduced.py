

from machineconfig.utils.utils2 import randstr
from datetime import datetime
import time
from pathlib import Path
import sys
import subprocess
from platform import system
from typing import Any, Optional, Union, Callable, TypeAlias, Literal
import os


OPLike: TypeAlias = Union[str, 'P', Path, None]
PLike: TypeAlias = Union[str, 'P', Path]
FILE_MODE: TypeAlias = Literal['r', 'w', 'x', 'a']
SHUTIL_FORMATS: TypeAlias = Literal["zip", "tar", "gztar", "bztar", "xztar"]


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
            Path.home().joinpath('dotfiles/creds/data/encrypted_files_key.bytes').write_bytes(key_resolved)
        else:
            try:
                key_resolved = Path.home().joinpath("dotfiles/creds/data/encrypted_files_key.bytes").read_bytes()
                print(f"⚠️ Using key from: {Path.home().joinpath('dotfiles/creds/data/encrypted_files_key.bytes')}")
            except FileNotFoundError as err:
                print("\n" * 3, "~" * 50, """Consider Loading up your dotfiles or pass `gen_key=True` to make and save one.""", "~" * 50, "\n" * 3)
                raise FileNotFoundError(err) from err
    elif isinstance(key, (str, P, Path)): key_resolved = Path(key).read_bytes()  # a path to a key file was passed, read it:
    elif type(key) is bytes: key_resolved = key  # key passed explicitly
    else: raise TypeError("❌ Key must be either a path, bytes object or None.")
    code = Fernet(key=key_resolved).encrypt(msg)
    if pwd is not None and salt is not None and iteration is not None: return base64.urlsafe_b64encode(b'%b%b%b' % (salt, iteration.to_bytes(4, 'big'), base64.urlsafe_b64decode(code)))
    return code
def decrypt(token: bytes, key: Optional[bytes] = None, pwd: Optional[str] = None, salted: bool = True) -> bytes:
    import base64
    if pwd is not None:
        assert key is None, "❌ You can either pass key or pwd, or none of them, but not both."
        if salted:
            decoded = base64.urlsafe_b64decode(token)
            salt, iterations, token = decoded[:16], decoded[16:20], base64.urlsafe_b64encode(decoded[20:])
            key_resolved = pwd2key(password=pwd, salt=salt, iterations=int.from_bytes(bytes=iterations, byteorder='big'))
        else: key_resolved = pwd2key(password=pwd)  # trailing `;` prevents IPython from caching the result.
    elif type(key) is bytes:
        assert pwd is None, "❌ You can either pass key or pwd, or none of them, but not both."
        key_resolved = key  # passsed explicitly
    elif key is None: key_resolved = Path.home().joinpath("dotfiles/creds/data/encrypted_files_key.bytes").read_bytes()  # read from file
    elif isinstance(key, (str, Path)): key_resolved = Path(key).read_bytes()  # passed a path to a file containing kwy
    else: raise TypeError(f"❌ Key must be either str, P, Path, bytes or None. Recieved: {type(key)}")
    from cryptography.fernet import Fernet
    return Fernet(key=key_resolved).decrypt(token)

def validate_name(astring: str, replace: str = '_') -> str:
    import re
    return re.sub(r'[^-a-zA-Z0-9_.()]+', replace, str(astring))
def timestamp(fmt: Optional[str] = None, name: Optional[str] = None) -> str:
    return ((name + '_') if name is not None else '') + datetime.now().strftime(fmt or '%Y-%m-%d-%I-%M-%S-%p-%f')  # isoformat is not compatible with file naming convention, fmt here is.


def modify_text(txt_raw: str, txt_search: str, txt_alt: Union[str, Callable[[str], str]], replace_line: bool = True, notfound_append: bool = False, prepend: bool = False, strict: bool = False):
    lines, bingo = txt_raw.split("\n"), False
    if not replace_line:  # no need for line splitting
        assert isinstance(txt_alt, str), f"txt_alt must be a string if notfound_append is True. It is not: {txt_alt}"
        if txt_search in txt_raw: return txt_raw.replace(txt_search, txt_alt)
        return txt_raw + "\n" + txt_alt if notfound_append else txt_raw
    for idx, line in enumerate(lines):
        if txt_search in line:
            if isinstance(txt_alt, str): lines[idx] = txt_alt
            elif callable(txt_alt): lines[idx] = txt_alt(line)
            bingo = True
    if strict and not bingo: raise ValueError(f"txt_search `{txt_search}` not found in txt_raw `{txt_raw}`")
    if bingo is False and notfound_append is True:
        assert isinstance(txt_alt, str), f"txt_alt must be a string if notfound_append is True. It is not: {txt_alt}"
        if prepend: lines.insert(0, txt_alt)
        else: lines.append(txt_alt)  # txt not found, add it anyway.
    return "\n".join(lines)


class Compression:
    @staticmethod
    def compress_folder(root_dir: str, op_path: str, base_dir: str, fmt: SHUTIL_FORMATS = 'zip', verbose: bool = False, **kwargs: Any) -> str:  # shutil works with folders nicely (recursion is done interally) # directory to be archived: root_dir\base_dir, unless base_dir is passed as absolute path. # when archive opened; base_dir will be found."""
        base_name = op_path[:-4] if op_path.endswith(".zip") else op_path  # .zip is added automatically by library, hence we'd like to avoid repeating it if user sent it.
        import shutil
        return shutil.make_archive(base_name=base_name, format=fmt, root_dir=root_dir, base_dir=base_dir, verbose=verbose, **kwargs)  # returned path possible have added extension.
    @staticmethod
    def zip_file(ip_path: str, op_path: str, arcname: Optional[str]= None, password: Optional[bytes] = None, mode: FILE_MODE = "w", **kwargs: Any):
        """arcname determines the directory of the file being archived inside the archive. Defaults to same as original directory except for drive.
        When changed, it should still include the file path in its end. If arcname = filename without any path, then, it will be in the root of the archive."""
        import zipfile
        with zipfile.ZipFile(op_path, mode=mode) as jungle_zip:
            if password is not None: jungle_zip.setpassword(pwd=password)
            jungle_zip.write(filename=str(ip_path), arcname=str(arcname) if arcname is not None else None, compress_type=zipfile.ZIP_DEFLATED, **kwargs)
        return Path(op_path)
    @staticmethod
    def unzip(ip_path: str, op_path: str, fname: Optional[str]= None, password: Optional[bytes] = None, memory: bool = False, **kwargs: Any) -> Path | dict[str, bytes] | bytes:
        import zipfile
        with zipfile.ZipFile(str(ip_path), 'r') as zipObj:
            if memory:
                return {name: zipObj.read(name) for name in zipObj.namelist()} if fname is None else zipObj.read(fname)
            if fname is None:
                zipObj.extractall(op_path, pwd=password, **kwargs)
                return Path(op_path)
            else:
                zipObj.extract(member=str(fname), path=str(op_path), pwd=password)
                return Path(op_path) / fname
    @staticmethod
    def gz(file: str, op_path: str):  # see this on what to use: https://stackoverflow.com/questions/10540935/what-is-the-difference-between-tar-and-zip
        import shutil
        import gzip
        with open(file, 'rb') as f_in:
            with gzip.open(op_path, 'wb') as f_out: shutil.copyfileobj(f_in, f_out)
        return Path(op_path)
    @staticmethod
    def ungz(path: str, op_path: str):
        import gzip
        import shutil
        with gzip.open(path, 'r') as f_in, open(op_path, 'wb') as f_out: shutil.copyfileobj(f_in, f_out)
        return Path(op_path)
    @staticmethod
    def unbz(path: str, op_path: str):
        import bz2
        import shutil
        with bz2.BZ2File(path, 'r') as fr, open(str(op_path), 'wb') as fw: shutil.copyfileobj(fr, fw)
        return Path(op_path)
    @staticmethod
    def xz(path: str, op_path: str):
        import lzma
        with lzma.open(op_path, "w") as f: f.write(Path(path).read_bytes())
    @staticmethod
    def unxz(ip_path: str, op_path: str):
        import lzma
        with lzma.open(ip_path) as file: Path(op_path).write_bytes(file.read())
    @staticmethod
    def tar(path: str, op_path: str):
        import tarfile
        with tarfile.open(op_path, "w:gz") as tar_: tar_.add(str(path), arcname=os.path.basename(path))
        return Path(op_path)
    @staticmethod
    def untar(path: str, op_path: str, fname: Optional[str]= None, mode: Literal['r', 'w'] = 'r', **kwargs: Any):
        import tarfile
        with tarfile.open(str(path), mode) as file:
            if fname is None: file.extractall(path=op_path, **kwargs)  # extract all files in the archive
            else: file.extract(fname, **kwargs)
        return Path(op_path)



class P(type(Path()), Path):  # type: ignore # pylint: disable=E0241
    # ============= Path management ==================
    """ The default behaviour of methods acting on underlying disk object is to perform the action and return a new path referring to the mutated object in disk drive.
    However, there is a flag `orig` that makes the function return orignal path object `self` as opposed to the new one pointing to new object.
    Additionally, the fate of the original object can be decided by a flag `inplace` which means `replace` it defaults to False and in essence, it deletes the original underlying object.
    This can be seen in `zip` and `encrypt` but not in `copy`, `move`, `retitle` because the fate of original file is dictated already.
    Furthermore, those methods are accompanied with print statement explaining what happened to the object."""
    def delete(self, sure: bool = False, verbose: bool = True) -> 'P':  # slf = self.expanduser().resolve() don't resolve symlinks.
        if not sure:
            if verbose: print(f"❌ Did NOT DELETE because user is not sure. file: {repr(self)}.")
            return self
        if not self.exists():
            self.unlink(missing_ok=True)
            if verbose: print(f"❌ Could NOT DELETE nonexisting file {repr(self)}. ")
            return self  # broken symlinks exhibit funny existence behaviour, catch them here.
        if self.is_file() or self.is_symlink(): self.unlink(missing_ok=True)
        else:
            import shutil
            shutil.rmtree(self, ignore_errors=False)
        if verbose: print(f"🗑️ ❌ DELETED {repr(self)}.")
        return self
    def move(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, rel2it: bool = False, overwrite: bool = False, verbose: bool = True, parents: bool = True, content: bool = False) -> 'P':
        path = self._resolve_path(folder=folder, name=name, path=path, default_name=self.absolute().name, rel2it=rel2it)
        if parents: path.parent.mkdir(parents=True, exist_ok=True)
        slf = self.expanduser().resolve()
        if content:
            assert self.is_dir(), NotADirectoryError(f"💥 When `content` flag is set to True, path must be a directory. It is not: `{repr(self)}`")
            [x.move(folder=path.parent, content=False, overwrite=overwrite) for x in self.search("*")]
            return path  # contents live within this directory.
        if overwrite:
            tmp_path = slf.rename(path.parent.absolute() / randstr())
            path.delete(sure=True, verbose=verbose)
            tmp_path.rename(path)  # works if moving a path up and parent has same name
        else:
            try:
                slf.rename(path)  # self._return(res=path, inplace=True, operation='rename', orig=False, verbose=verbose, strict=True, msg='')
            except OSError as oe: # OSError: [Errno 18] Invalid cross-device link:
                # https://stackoverflow.com/questions/42392600/oserror-errno-18-invalid-cross-device-link
                import shutil
                shutil.move(str(slf), str(path))
                _ = oe
        if verbose: print(f"🚚 MOVED {repr(self)} ==> {repr(path)}`")
        return path
    def copy(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, content: bool = False, verbose: bool = True, append: Optional[str] = None, overwrite: bool = False, orig: bool = False) -> 'P':  # tested %100  # TODO: replace `content` flag with ability to interpret "*" in resolve method.
        dest = self._resolve_path(folder=folder, name=name, path=path, default_name=self.name, rel2it=False)
        dest = dest.expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        slf = self.expanduser().resolve()
        if dest == slf:
            dest = self.append(append if append is not None else f"_copy_{randstr()}")
        if not content and overwrite and dest.exists(): dest.delete(sure=True)
        if not content and not overwrite and dest.exists(): raise FileExistsError(f"💥 Destination already exists: {repr(dest)}")
        if slf.is_file():
            import shutil
            shutil.copy(str(slf), str(dest))
            if verbose: print(f"🖨️ COPIED {repr(slf)} ==> {repr(dest)}")
        elif slf.is_dir():
            dest = dest.parent if content else dest
            # from distutils.dir_util import copy_tree
            from shutil import copytree
            copytree(str(slf), str(dest))
            if verbose: print(f"🖨️ COPIED {'Content of ' if content else ''} {repr(slf)} ==> {repr(dest)}")
        else: print(f"💥 Could NOT COPY. Not a file nor a path: {repr(slf)}.")
        return dest if not orig else self
    # ======================================= File Editing / Reading ===================================
    def download(self, folder: OPLike = None, name: Optional[str]= None, allow_redirects: bool = True, timeout: Optional[int] = None, params: Any = None) -> 'P':
        import requests
        response = requests.get(self.as_url_str(), allow_redirects=allow_redirects, timeout=timeout, params=params)  # Alternative: from urllib import request; request.urlopen(url).read().decode('utf-8').
        assert response.status_code == 200, f"Download failed with status code {response.status_code}\n{response.text}"
        if name is not None: f_name = name
        else:
            try:
                f_name = response.headers['Content-Disposition'].split('filename=')[1].replace('"', '')
            except (KeyError, IndexError):
                f_name = validate_name(str(P(response.history[-1].url).name if len(response.history) > 0 else P(response.url).name))
        dest_path = (P.home().joinpath("Downloads") if folder is None else P(folder)).joinpath(f_name)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(response.content)
        return dest_path
    def _return(self, res: Union['P', 'Path'], operation: Literal['rename', 'delete', 'Whack'], inplace: bool = False, overwrite: bool = False, orig: bool = False, verbose: bool = False, strict: bool = True, msg: str = "", __delayed_msg__: str = "") -> 'P':
        res = P(res)
        if inplace:
            assert self.exists(), f"`inplace` flag is only relevant if the path exists. It doesn't {self}"
            if operation == "rename":
                if overwrite and res.exists(): res.delete(sure=True, verbose=verbose)
                if not overwrite and res.exists():
                    if strict: raise FileExistsError(f"❌ RENAMING failed. File `{res}` already exists.")
                    else:
                        if verbose: print(f"⚠️ SKIPPED RENAMING {repr(self)} ➡️ {repr(res)} because FileExistsError and scrict=False policy.")
                        return self if orig else res
                self.rename(res)
                msg = msg or f"RENAMED {repr(self)} ➡️ {repr(res)}"
            elif operation == "delete":
                self.delete(sure=True, verbose=False)
                __delayed_msg__ = f"DELETED 🗑️❌ {repr(self)}."
        if verbose and msg != "":
            try: print(msg)  # emojie print error.
            except UnicodeEncodeError: print("P._return warning: UnicodeEncodeError, could not print message.")
        if verbose and __delayed_msg__ != "":
            try: print(__delayed_msg__)
            except UnicodeEncodeError: print("P._return warning: UnicodeEncodeError, could not print message.")
        return self if orig else res
    def append(self, name: str = '', index: bool = False, suffix: Optional[str] = None, verbose: bool = True, **kwargs: Any) -> 'P':
        """Returns a new path object with the name appended to the stem of the path. If `index` is True, the name will be the index of the path in the parent directory."""
        if index:
            appended_name = f'''{name}_{len(self.parent.search(f"*{self.name.split('.')[0]}*"))}'''
            return self.append(name=appended_name, index=False, verbose=verbose, suffix=suffix, **kwargs)
        full_name = (name or ("_" + str(timestamp())))
        full_suffix = suffix or ''.join(('bruh' + self).suffixes)
        subpath = self.name.split('.')[0] + full_name + full_suffix
        return self._return(self.parent.joinpath(subpath), operation="rename", verbose=verbose, **kwargs)
    def with_name(self, name: str, verbose: bool = True, inplace: bool = False, overwrite: bool = False, **kwargs: Any):
        return self._return(self.parent / name, verbose=verbose, operation="rename", inplace=inplace, overwrite=overwrite, **kwargs)
    def __deepcopy__(self, *args: Any, **kwargs: Any) -> 'P':
        _ = args, kwargs
        return P(str(self))
    def __getstate__(self) -> str: return str(self)
    def __add__(self, other: PLike) -> 'P':
        return self.parent.joinpath(self.name + str(other))  # used append and prepend if the addition wanted to be before suffix.
    def __radd__(self, other: PLike) -> 'P':
        return self.parent.joinpath(str(other) + self.name)  # other + P and `other` doesn't know how to make this addition.
    def __sub__(self, other: PLike) -> 'P':
        res = P(str(self).replace(str(other), ""))
        return (res[1:] if str(res[0]) in {"\\", "/"} else res) if len(res.parts) else res  # paths starting with "/" are problematic. e.g ~ / "/path" doesn't work.

    def rel2home(self, ) -> 'P': return self._return(P(self.expanduser().absolute().relative_to(Path.home())), operation='Whack')  # very similat to collapseuser but without "~" being added so its consistent with rel2cwd.
    def collapseuser(self, strict: bool = True, placeholder: str = "~") -> 'P':  # opposite of `expanduser` resolve is crucial to fix Windows cases insensitivty problem.
        if strict: assert str(self.expanduser().absolute().resolve()).startswith(str(P.home())), ValueError(f"`{P.home()}` is not in the subpath of `{self}`")
        if (str(self).startswith(placeholder) or P.home().as_posix() not in self.resolve().as_posix()): return self
        return self._return(res=P(placeholder) / (self.expanduser().absolute().resolve(strict=strict) - P.home()), operation='Whack')  # resolve also solves the problem of Windows case insensitivty.
    def __getitem__(self, slici: Union[int, list[int], slice]):
        if isinstance(slici, list): return P(*[self[item] for item in slici])
        elif isinstance(slici, int): return P(self.parts[slici])
        return P(*self.parts[slici])  # must be a slice
    def split(self, at: Optional[str] = None, index: Optional[int] = None, sep: Literal[-1, 0, 1] = 1, strict: bool = True):
        if index is None and at is not None:  # at is provided  # ====================================   Splitting
            if not strict:  # behaves like split method of string
                one, two = (items := str(self).split(sep=str(at)))[0], items[1]
                one, two = P(one[:-1]) if one.endswith("/") else P(one), P(two[1:]) if two.startswith("/") else P(two)
            else:  # "strict": # raises an error if exact match is not found.
                index = self.parts.index(str(at))
                one, two = self[0:index], self[index + 1:]  # both one and two do not include the split item.
        elif index is not None and at is None:  # index is provided
            one, two = self[:index], P(*self.parts[index + 1:])
            at = self.parts[index]  # this is needed below.
        else: raise ValueError("Either `index` or `at` can be provided. Both are not allowed simulatanesouly.")
        if sep == 0: return one, two  # neither of the portions get the sperator appended to it. # ================================  appending `at` to one of the portions
        elif sep == 1: return one, P(at) / two   # append it to right portion
        elif sep == -1:
            return one / at, two  # append it to left portion.
        else: raise ValueError(f"`sep` should take a value from the set [-1, 0, 1] but got {sep}")
    def __repr__(self):  # this is useful only for the console
        if self.is_symlink():
            try: target = self.resolve()  # broken symolinks are funny, and almost always fail `resolve` method.
            except Exception: target = "BROKEN LINK " + str(self)  # avoid infinite recursions for broken links.
            return "🔗 Symlink '" + str(self) + "' ==> " + (str(target) if target == self else str(target))
        elif self.is_absolute(): return self._type() + " '" + str(self.clickable()) + "'" + (" | " + self.time(which="c").isoformat()[:-7].replace("T", "  ") if self.exists() else "") + (f" | {self.size()} Mb" if self.is_file() else "")
        elif "http" in str(self): return "🕸️ URL " + str(self.as_url_str())
        else: return "📍 Relative " + "'" + str(self) + "'"  # not much can be said about a relative path.
    # def to_str(self) -> str: return str(self)
    def size(self, units: Literal['b', 'kb', 'mb', 'gb'] = 'mb') -> float:  # ===================================== File Specs ==========================================================================================
        total_size = self.stat().st_size if self.is_file() else sum([item.stat().st_size for item in self.rglob("*") if item.is_file()])
        tmp: int
        match units:
            case "b": tmp = 1024 ** 0
            case "kb": tmp = 1024 ** 1
            case "mb": tmp = 1024 ** 2
            case "gb": tmp = 1024 ** 3
        return round(number=total_size / tmp, ndigits=1)
    def time(self, which: Literal["m", "c", "a"] = "m", **kwargs: Any):
        """* `m`: last mofidication of content, i.e. the time it was created.
        * `c`: last status change (its inode is changed, permissions, path, but not content)
        * `a`: last access (read)
        """
        match which:
            case "m": tmp = self.stat().st_mtime
            case "a": tmp = self.stat().st_atime
            case "c": tmp = self.stat().st_ctime
        return datetime.fromtimestamp(tmp, **kwargs)

    # ================================ String Nature management ====================================
    def clickable(self, ) -> 'P': return self._return(res=P(self.expanduser().resolve().as_uri()), operation='Whack')
    def as_url_str(self) -> 'str': return self.as_posix().replace("https:/", "https://").replace("http:/", "http://")
    def as_zip_path(self):
        import zipfile
        res = self.expanduser().resolve()
        return zipfile.Path(res)  # .str.split(".zip") tmp=res[1]+(".zip" if len(res) > 2 else ""); root=res[0]+".zip", at=P(tmp).as_posix())  # TODO
    # ========================== override =======================================
    def __setitem__(self, key: Union['str', int, slice], value: PLike):
        fullparts, new = list(self.parts), list(P(value).parts)
        if type(key) is str:
            idx = fullparts.index(key)
            fullparts.remove(key)
            fullparts = fullparts[:idx] + new + fullparts[idx + 1:]
        elif type(key) is int: fullparts = fullparts[:key] + new + fullparts[key + 1:]
        elif type(key) is slice: fullparts = fullparts[:(0 if key.start is None else key.start)] + new + fullparts[(len(fullparts) if key.stop is None else key.stop):]
        self._str = str(P(*fullparts))  # pylint: disable=W0201  # similar attributes: # self._parts # self._pparts # self._cparts # self._cached_cparts

    def _type(self):
        if self.absolute():
            if self.is_file(): return "📄"
            elif self.is_dir(): return "📁"
            return "👻NotExist"
        return "📍Relative"
    def symlink_to(self, target: PLike, verbose: bool = True, overwrite: bool = False, orig: bool = False, strict: bool = True):  # type: ignore[override]  # pylint: disable=W0237
        self.parent.mkdir(parents=True, exist_ok=True)
        target_obj = P(target).expanduser().resolve()
        if strict: assert target_obj.exists(), f"Target path `{target}` (aka `{target_obj}`) doesn't exist. This will create a broken link."
        if overwrite and (self.is_symlink() or self.exists()): self.delete(sure=True, verbose=verbose)
        from machineconfig.utils.terminal import Terminal
        if system() == "Windows" and not Terminal.is_user_admin():  # you cannot create symlink without priviliages.
            import win32com.shell.shell
            _proce_info = win32com.shell.shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=f" -c \"from pathlib import Path; Path(r'{self.expanduser()}').symlink_to(r'{str(target_obj)}')\"")
            # TODO update PATH for this to take effect immediately.
            time.sleep(1)  # wait=True equivalent
        else: super(P, self.expanduser()).symlink_to(str(target_obj))
        return self._return(target_obj, operation='Whack', inplace=False, orig=orig, verbose=verbose, msg=f"LINKED {repr(self)} ➡️ {repr(target_obj)}")
    def resolve(self, strict: bool = False):
        try: return super(P, self).resolve(strict=strict)
        except OSError: return self
    # ======================================== Folder management =======================================
    def search(self, pattern: str = '*', r: bool = False, files: bool = True, folders: bool = True, compressed: bool = False, dotfiles: bool = False, filters_total: Optional[list[Callable[[Any], bool]]] = None, not_in: Optional[list[str]] = None,
               exts: Optional[list[str]] = None, win_order: bool = False) -> list['P']:
        if isinstance(not_in, list):
            filters_notin = [lambda x: all([str(a_not_in) not in str(x) for a_not_in in not_in])]  # type: ignore
        else: filters_notin = []
        if isinstance(exts, list):
            filters_extension = [lambda x: any([ext in x.name for ext in exts])]  # type: ignore
        else: filters_extension = []
        filters_total = (filters_total or []) + filters_notin + filters_extension
        if not files: filters_total.append(lambda x: x.is_dir())
        if not folders: filters_total.append(lambda x: x.is_file())
        slf = self.expanduser().resolve()
        if ".zip" in str(slf) and compressed:  # the root (self) is itself a zip archive (as opposed to some search results are zip archives)
            import zipfile
            import fnmatch
            root = slf.as_zip_path()
            if not r:
                raw = list(root.iterdir())
            else:
                raw = [root.joinpath(item) for item in zipfile.ZipFile(str(slf)).namelist()]
            # res1 = raw.filter(lambda zip_path: fnmatch.fnmatch(zip_path.at, pattern))  # type: ignore
            res1 = [item for item in raw if fnmatch.fnmatch(item.at, pattern)]
            # return res1.filter(lambda x: (folders or x.is_file()) and (files or x.is_dir()))
            return [item for item in res1 if (folders or item.is_file()) and (files or item.is_dir())]  # type: ignore
        elif dotfiles: raw = slf.glob(pattern) if not r else self.rglob(pattern)
        else:
            from glob import glob
            if r:
                raw = glob(str(slf / "**" / pattern), recursive=r)
            else:
                raw = glob(str(slf.joinpath(pattern)))  # glob ignroes dot and hidden files
        if ".zip" not in str(slf) and compressed:
            filters_notin = [P(comp_file).search(pattern=pattern, r=r, files=files, folders=folders, compressed=True, dotfiles=dotfiles, filters_total=filters_total, not_in=not_in, win_order=win_order) for comp_file in self.search("*.zip", r=r)]
            from functools import reduce
            # haha = List(filters_notin).reduce(func=lambda x, y: x + y)
            haha = reduce(lambda x, y: x + y, filters_notin) if len(filters_notin) else []
            raw = raw + haha  # type: ignore
        processed = []
        for item in raw:
            item_ = P(item)
            if all([afilter(item_) for afilter in filters_total]):
                processed.append(item_)
        if not win_order: return list(processed)
        import re
        processed.sort(key=lambda x: [int(k) if k.isdigit() else k for k in re.split('([0-9]+)', string=x.stem)])
        return list(processed)
    @staticmethod
    def tmpdir(prefix: str = "") -> 'P':
        return P.tmp(folder=rf"tmp_dirs/{prefix + ('_' if prefix != '' else '') + randstr()}")
    @staticmethod
    def tmpfile(name: Optional[str]= None, suffix: str = "", folder: OPLike = None, tstamp: bool = False, noun: bool = False) -> 'P':
        name_concrete = name or randstr(noun=noun)
        return P.tmp(file=name_concrete + "_" + randstr() + (("_" + str(timestamp())) if tstamp else "") + suffix, folder=folder or "tmp_files")
    @staticmethod
    def tmp(folder: OPLike = None, file: Optional[str] = None, root: str = "~/tmp_results") -> 'P':
        base = P(root).expanduser().joinpath(folder or "").joinpath(file or "")
        target_path = base.parent if file else base
        target_path.mkdir(parents=True, exist_ok=True)
        return base
    # ====================================== Compression & Encryption ===========================================
    def zip(self, path: OPLike = None, folder: OPLike = None, name: Optional[str]= None, arcname: Optional[str] = None, inplace: bool = False, verbose: bool = True,
            content: bool = False, orig: bool = False, pwd: Optional[str] = None, mode: FILE_MODE = 'w', **kwargs: Any) -> 'P':
        path_resolved, slf = self._resolve_path(folder, name, path, self.name).expanduser().resolve(), self.expanduser().resolve()
        # if use_7z:  # benefits over regular zip and encrypt: can handle very large files with low memory footprint
        #     path_resolved = path_resolved + '.7z' if not path_resolved.suffix == '.7z' else path_resolved
        #     with install_n_import("py7zr").SevenZipFile(file=path_resolved, mode=mode, password=pwd) as archive: archive.writeall(path=str(slf), arcname=None)
        arcname_obj = P(arcname or slf.name)
        if arcname_obj.name != slf.name: arcname_obj /= slf.name  # arcname has to start from somewhere and end with filename
        if slf.is_file():
            path_resolved = Compression.zip_file(ip_path=str(slf), op_path=str(path_resolved + ".zip" if path_resolved.suffix != ".zip" else path_resolved), arcname=str(arcname_obj), mode=mode, **kwargs)
        else:
            if content: root_dir, base_dir = slf, "."
            else: root_dir, base_dir = slf.split(at=str(arcname_obj[0]), sep=1)[0], str(arcname_obj)
            path_resolved = P(Compression.compress_folder(root_dir=str(root_dir), op_path=str(path_resolved), base_dir=base_dir, fmt='zip', **kwargs))  # TODO: see if this supports mode
        return self._return(path_resolved, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"ZIPPED {repr(slf)} ==>  {repr(path)}")
    def unzip(self, folder: OPLike = None, path: OPLike = None, name: Optional[str]= None, verbose: bool = True, content: bool = False, inplace: bool = False, overwrite: bool = False, orig: bool = False,
              pwd: Optional[str] = None, tmp: bool = False, pattern: Optional[str] = None, merge: bool = False) -> 'P':
        assert merge is False, "I have not implemented this yet"
        assert path is None, "I have not implemented this yet"
        if tmp: return self.unzip(folder=P.tmp().joinpath("tmp_unzips").joinpath(randstr()), content=True).joinpath(self.stem)
        slf = zipfile__ = self.expanduser().resolve()
        if any(ztype in str(slf.parent) for ztype in (".zip", ".7z")):  # path include a zip archive in the middle.
            tmp__ = [item for item in (".zip", ".7z", "") if item in str(slf)]
            ztype = tmp__[0]
            if ztype == "": return slf
            # zipfile__, name__ = slf.split(at=str(List(slf.parts).filter(lambda x: ztype in x)[0]), sep=-1)
            zipfile__, name__ = slf.split(at=str(next(item for item in slf.parts if ztype in item)), sep=-1)
            name = str(name__)
        folder = (zipfile__.parent / zipfile__.stem) if folder is None else P(folder).expanduser().absolute().resolve().joinpath(zipfile__.stem)
        assert isinstance(folder, P), "folder should be a P object at this point"
        folder = folder if not content else folder.parent
        if slf.suffix == ".7z":
            raise NotImplementedError("I have not implemented this yet")
            # if overwrite: P(folder).delete(sure=True)
            # result = folder
            # import py7zr
            # with py7zr.SevenZipFile(file=slf, mode='r', password=pwd) as archive:
            #     if pattern is not None:
            #         import re
            #         pat = re.compile(pattern)
            #         archive.extract(path=folder, targets=[f for f in archive.getnames() if pat.match(f)])
            #     else: archive.extractall(path=folder)
        else:
            if overwrite:
                if not content: P(folder).joinpath(name or "").delete(sure=True, verbose=True)  # deletes a specific file / folder that has the same name as the zip file without extension.
                else:
                    import zipfile
                    mylist = [x for x in zipfile.ZipFile(str(self)).namelist() if "/" not in x or (len(x.split('/')) == 2 and x.endswith("/"))]
                    # List().apply(lambda item: P(folder).joinpath(name or "", item.replace("/", "")).delete(sure=True, verbose=True))
                    for item in mylist: P(folder).joinpath(name or "", item.replace("/", "")).delete(sure=True, verbose=True)
            result = Compression.unzip(str(zipfile__), str(folder), None if name is None else P(name).as_posix())
            assert isinstance(result, Path)
        return self._return(P(result), inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"UNZIPPED {repr(zipfile__)} ==> {repr(result)}")
    def untar(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> 'P':
        op_path = self._resolve_path(folder, name, path, self.name.replace(".tar", "")).expanduser().resolve()
        Compression.untar(str(self.expanduser().resolve()), op_path=str(op_path))
        return self._return(op_path, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"UNTARRED {repr(self)} ==>  {repr(op_path)}")
    def ungz(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> 'P':
        op_path = self._resolve_path(folder, name, path, self.name.replace(".gz", "")).expanduser().resolve()
        Compression.ungz(str(self.expanduser().resolve()), op_path=str(op_path))
        return self._return(op_path, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"UNGZED {repr(self)} ==>  {repr(op_path)}")
    def unxz(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> 'P':
        op_path = self._resolve_path(folder, name, path, self.name.replace(".xz", "")).expanduser().resolve()
        Compression.unxz(str(self.expanduser().resolve()), op_path=str(op_path))
        return self._return(op_path, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"UNXZED {repr(self)} ==>  {repr(op_path)}")
    def unbz(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> 'P':
        op_path = self._resolve_path(folder=folder, name=name, path=path, default_name=self.name.replace(".bz", "").replace(".tbz", ".tar")).expanduser().resolve()
        Compression.unbz(str(self.expanduser().resolve()), op_path=str(op_path))
        return self._return(op_path, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"UNBZED {repr(self)} ==>  {repr(op_path)}")
    def decompress(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, inplace: bool = False, orig: bool = False, verbose: bool = True) -> 'P':
        if ".tar.gz" in str(self) or ".tgz" in str(self):
            # res = self.ungz_untar(folder=folder, path=path, name=name, inplace=inplace, verbose=verbose, orig=orig)
            return self.ungz(name=f"tmp_{randstr()}.tar", inplace=inplace).untar(folder=folder, name=name, path=path, inplace=True, orig=orig, verbose=verbose)  # this works for .tgz suffix as well as .tar.gz
        elif ".gz" in str(self): res = self.ungz(folder=folder, path=path, name=name, inplace=inplace, verbose=verbose, orig=orig)
        elif ".tar.bz" in str(self) or "tbz" in str(self):
            res = self.unbz(name=f"tmp_{randstr()}.tar", inplace=inplace)
            return res.untar(folder=folder, name=name, path=path, inplace=True, orig=orig, verbose=verbose)
        elif ".tar.xz" in str(self):
            # res = self.unxz_untar(folder=folder, path=path, name=name, inplace=inplace, verbose=verbose, orig=orig)
            res = self.unxz(inplace=inplace).untar(folder=folder, name=name, path=path, inplace=True, orig=orig, verbose=verbose)
        elif ".zip" in str(self): res = self.unzip(folder=folder, path=path, name=name, inplace=inplace, verbose=verbose, orig=orig)
        else: res = self
        return res
    def encrypt(self, key: Optional[bytes] = None, pwd: Optional[str] = None, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None,
                verbose: bool = True, suffix: str = ".enc", inplace: bool = False, orig: bool = False) -> 'P':
        # see: https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python & https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password"""
        slf = self.expanduser().resolve()
        path = self._resolve_path(folder, name, path, slf.name + suffix)
        assert slf.is_file(), f"Cannot encrypt a directory. You might want to try `zip_n_encrypt`. {self}"
        path.write_bytes(encrypt(msg=slf.read_bytes(), key=key, pwd=pwd))
        return self._return(path, inplace=inplace, operation="delete", orig=orig, verbose=verbose, msg=f"🔒🔑 ENCRYPTED: {repr(slf)} ==> {repr(path)}.")
    def decrypt(self, key: Optional[bytes] = None, pwd: Optional[str] = None, path: OPLike = None, folder: OPLike = None, name: Optional[str]= None, verbose: bool = True, suffix: str = ".enc", inplace: bool = False) -> 'P':
        slf = self.expanduser().resolve()
        path = self._resolve_path(folder=folder, name=name, path=path, default_name=slf.name.replace(suffix, "") if suffix in slf.name else "decrypted_" + slf.name)
        path.write_bytes(decrypt(token=slf.read_bytes(), key=key, pwd=pwd))
        return self._return(path, operation="delete", verbose=verbose, msg=f"🔓🔑 DECRYPTED: {repr(slf)} ==> {repr(path)}.", inplace=inplace)
    def zip_n_encrypt(self, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, verbose: bool = True, orig: bool = False, content: bool = False) -> 'P':
        return self.zip(inplace=inplace, verbose=verbose, content=content).encrypt(key=key, pwd=pwd, verbose=verbose, inplace=True) if not orig else self
    def decrypt_n_unzip(self, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, verbose: bool = True, orig: bool = False) -> 'P': return self.decrypt(key=key, pwd=pwd, verbose=verbose, inplace=inplace).unzip(folder=None, inplace=True, content=False) if not orig else self
    def _resolve_path(self, folder: OPLike, name: Optional[str], path: OPLike, default_name: str, rel2it: bool = False) -> 'P':
        """:param rel2it: `folder` or `path` are relative to `self` as opposed to cwd. This is used when resolving '../dir'"""
        if path is not None:
            path = P(self.joinpath(path).resolve() if rel2it else path).expanduser().resolve()
            assert folder is None and name is None, "If `path` is passed, `folder` and `name` cannot be passed."
            assert isinstance(path, P), "path should be a P object at this point"
            assert not path.is_dir(), f"`path` passed is a directory! it must not be that. If this is meant, pass it with `folder` kwarg. `{path}`"
            return path
        name, folder = (default_name if name is None else str(name)), (self.parent if folder is None else folder)  # good for edge cases of path with single part.  # means same directory, just different name
        return P(self.joinpath(folder).resolve() if rel2it else folder).expanduser().resolve() / name

    def get_remote_path(self, root: Optional[str], os_specific: bool = False, rel2home: bool = True, strict: bool = True) -> 'P':
        import platform
        tmp1: str = (platform.system().lower() if os_specific else 'generic_os')
        if not rel2home: path = self
        else:
            try: path = self.rel2home()
            except ValueError as ve:
                if strict: raise ve
                path = self
        # if obfuscate:
        #     msc.obfuscater import obfuscate as obfuscate_func
        #     name = obfuscate_func(seed=P.home().joinpath('dotfiles/creds/data/obfuscation_seed').read_text(encoding="utf-8").rstrip(), data=path.name)
        #     path = path.with_name(name=name)
        if isinstance(root, str):  # the following is to avoid the confusing behaviour of A.joinpath(B) if B is absolute.
            part1 = path.parts[0]
            if part1 == "/": sanitized_path = path[1:].as_posix()
            else: sanitized_path = path.as_posix()
            return P(root + "/" + tmp1 + "/" + sanitized_path)
        return tmp1 / path
    def to_cloud(self, cloud: str, remotepath: OPLike = None, zip: bool = False,encrypt: bool = False,  # pylint: disable=W0621, W0622
                 key: Optional[bytes] = None, pwd: Optional[str] = None, rel2home: bool = False, strict: bool = True,
                #  obfuscate: bool = False,
                 share: bool = False, verbose: bool = True, os_specific: bool = False, transfers: int = 10, root: Optional[str] = "myhome") -> 'P':
        to_del = []
        localpath = self.expanduser().absolute() if not self.exists() else self
        if zip:
            localpath = localpath.zip(inplace=False)
            to_del.append(localpath)
        if encrypt:
            localpath = localpath.encrypt(key=key, pwd=pwd, inplace=False)
            to_del.append(localpath)
        if remotepath is None:
            rp = localpath.get_remote_path(root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)  # if rel2home else (P(root) / localpath if root is not None else localpath)
        else: rp = P(remotepath)
        rclone_cmd = f"""rclone copyto '{localpath.as_posix()}' '{cloud}:{rp.as_posix()}' {'--progress' if verbose else ''} --transfers={transfers}"""
        from machineconfig.utils.terminal import Terminal
        if verbose: print(f"{'⬆️'*5} UPLOADING with `{rclone_cmd}`")
        shell_to_use = "powershell" if sys.platform == "win32" else "bash"
        res = Terminal(stdout=None if verbose else subprocess.PIPE).run(rclone_cmd, shell=shell_to_use).capture()
        _ = [item.delete(sure=True) for item in to_del]
        assert res.is_successful(strict_err=False, strict_returcode=True), res.print(capture=False, desc="Cloud Storage Operation")
        if verbose: print(f"{'⬆️'*5} UPLOAD COMPLETED.")
        if share:
            if verbose: print("🔗 SHARING FILE")
            shell_to_use = "powershell" if sys.platform == "win32" else "bash"
            res = Terminal().run(f"""rclone link '{cloud}:{rp.as_posix()}'""", shell=shell_to_use).capture()
            tmp = res.op2path(strict_err=False, strict_returncode=False)
            if tmp is None:
                res.print()
                raise RuntimeError(f"💥 Could not get link for {self}.")
            else:
                res.print_if_unsuccessful(desc="Cloud Storage Operation", strict_err=True, strict_returncode=True)
            link_p: 'P' = P(str(tmp))
            return link_p
        return self
    def from_cloud(self, cloud: str, remotepath: OPLike = None, decrypt: bool = False, unzip: bool = False,  # type: ignore  # pylint: disable=W0621
                   key: Optional[bytes] = None, pwd: Optional[str] = None, rel2home: bool = False, os_specific: bool = False, strict: bool = True,
                   transfers: int = 10, root: Optional[str] = "myhome", verbose: bool = True, overwrite: bool = True, merge: bool = False,):
        if remotepath is None:
            remotepath = self.get_remote_path(root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)
            remotepath += ".zip" if unzip else ""
            remotepath += ".enc" if decrypt else ""
        else: remotepath = P(remotepath)
        localpath = self.expanduser().absolute()
        localpath += ".zip" if unzip else ""
        localpath += ".enc" if decrypt else ""
        rclone_cmd = f"""rclone copyto '{cloud}:{remotepath.as_posix()}' '{localpath.as_posix()}' {'--progress' if verbose else ''} --transfers={transfers}"""
        from machineconfig.utils.terminal import Terminal
        if verbose: print(f"{'⬇️' * 5} DOWNLOADING with `{rclone_cmd}`")
        shell_to_use = "powershell" if sys.platform == "win32" else "bash"
        res = Terminal(stdout=None if verbose else subprocess.PIPE).run(rclone_cmd, shell=shell_to_use)
        success = res.is_successful(strict_err=False, strict_returcode=True)
        if not success:
            res.print(capture=False, desc="Cloud Storage Operation")
            return None
        if decrypt: localpath = localpath.decrypt(key=key, pwd=pwd, inplace=True)
        if unzip: localpath = localpath.unzip(inplace=True, verbose=True, overwrite=overwrite, content=True, merge=merge)
        return localpath
    def sync_to_cloud(self, cloud: str, sync_up: bool = False, sync_down: bool = False, os_specific: bool = False, rel2home: bool = True, transfers: int = 10, delete: bool = False, root: Optional[str] = "myhome", verbose: bool = True):
        tmp_path_obj = self.expanduser().absolute()
        tmp_path_obj.parent.mkdir(parents=True, exist_ok=True)
        tmp1, tmp2 = tmp_path_obj.as_posix(), self.get_remote_path(root=root, os_specific=os_specific).as_posix()
        source, target = (tmp1, f"{cloud}:{tmp2 if rel2home else tmp1}") if sync_up else (f"{cloud}:{tmp2 if rel2home else tmp1}", tmp1)  # in bisync direction is irrelavent.
        if not sync_down and not sync_up:
            _ = print(f"SYNCING 🔄️ {source} {'<>' * 7} {target}`") if verbose else None
            rclone_cmd = f"""rclone bisync '{source}' '{target}' --resync --remove-empty-dirs """
        else:
            print(f"SYNCING 🔄️ {source} {'>' * 15} {target}`")
            rclone_cmd = f"""rclone sync '{source}' '{target}' """
        rclone_cmd += f" --progress --transfers={transfers} --verbose"
        rclone_cmd += (" --delete-during" if delete else "")
        from machineconfig.utils.terminal import Terminal
        if verbose : print(rclone_cmd)
        shell_to_use = "powershell" if sys.platform == "win32" else "bash"
        res = Terminal(stdout=None if verbose else subprocess.PIPE).run(rclone_cmd, shell=shell_to_use)
        success = res.is_successful(strict_err=False, strict_returcode=True)
        if not success:
            res.print(capture=False, desc="Cloud Storage Operation")
            return None
        return self
