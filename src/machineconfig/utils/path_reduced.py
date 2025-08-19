# from crocodile.core import List, timestamp, randstr, validate_name, install_n_import
# from crocodile.file_management_helpers.file1 import encrypt, decrypt, modify_text
# from crocodile.file_management_helpers.file2 import Compression
# from crocodile.file_management_helpers.file5 import Read
# from pathlib import Path
# from datetime import datetime
# import os
# import sys
# import subprocess
# from typing import Any, Optional, Union, Callable, TypeAlias, Literal


# OPLike: TypeAlias = Union[str, 'PathReduced', Path, None]
# PLike: TypeAlias = Union[str, 'PathReduced', Path]
# FILE_MODE: TypeAlias = Literal['r', 'w', 'x', 'a']
# SHUTIL_FORMATS: TypeAlias = Literal["zip", "tar", "gztar", "bztar", "xztar"]


# class PathReduced(type(Path()), Path):  # type: ignore # pylint: disable=E0241
#     """Reduced version of the P class with only the most commonly used methods."""
    
#     # ============= Core Methods from used_methods.md ==================
    
#     def delete(self, sure: bool = False, verbose: bool = True) -> 'PathReduced':
#         if not sure:
#             if verbose: print(f"❌ Did NOT DELETE because user is not sure. file: {repr(self)}.")
#             return self
#         if not self.exists():
#             self.unlink(missing_ok=True)
#             if verbose: print(f"❌ Could NOT DELETE nonexisting file {repr(self)}. ")
#             return self  # broken symlinks exhibit funny existence behaviour, catch them here.
#         if self.is_file() or self.is_symlink(): self.unlink(missing_ok=True)
#         else:
#             import shutil
#             shutil.rmtree(self, ignore_errors=False)
#         if verbose: print(f"🗑️ ❌ DELETED {repr(self)}.")
#         return self

#     def search(self, pattern: str = '*', r: bool = False, files: bool = True, folders: bool = True, compressed: bool = False, dotfiles: bool = False, filters_total: Optional[list[Callable[[Any], bool]]] = None, not_in: Optional[list[str]] = None,
#                exts: Optional[list[str]] = None, win_order: bool = False) -> List['PathReduced']:
#         if isinstance(not_in, list):
#             filters_notin = [lambda x: all([str(a_not_in) not in str(x) for a_not_in in not_in])]  # type: ignore
#         else: filters_notin = []
#         if isinstance(exts, list):
#             filters_extension = [lambda x: any([ext in x.name for ext in exts])]  # type: ignore
#         else: filters_extension = []
#         filters_total = (filters_total or []) + filters_notin + filters_extension
#         if not files: filters_total.append(lambda x: x.is_dir())
#         if not folders: filters_total.append(lambda x: x.is_file())
#         if ".zip" in (slf := self.expanduser().resolve()) and compressed:  # the root (self) is itself a zip archive (as opposed to some search results are zip archives)
#             import zipfile
#             import fnmatch
#             root = slf.as_zip_path()
#             if not r:
#                 raw = List(root.iterdir())
#             else:
#                 raw = List(zipfile.ZipFile(str(slf)).namelist()).apply(root.joinpath)
#             res1 = raw.filter(lambda zip_path: fnmatch.fnmatch(zip_path.at, pattern))  # type: ignore
#             return res1.filter(lambda x: (folders or x.is_file()) and (files or x.is_dir()))  # type: ignore
#         elif dotfiles: raw = slf.glob(pattern) if not r else self.rglob(pattern)
#         else:
#             from glob import glob
#             if r:
#                 raw = glob(str(slf / "**" / pattern), recursive=r)
#             else:
#                 raw = glob(str(slf.joinpath(pattern)))  # glob ignroes dot and hidden files
#         if ".zip" not in slf and compressed:
#             filters_notin = [PathReduced(comp_file).search(pattern=pattern, r=r, files=files, folders=folders, compressed=True, dotfiles=dotfiles, filters_total=filters_total, not_in=not_in, win_order=win_order) for comp_file in self.search("*.zip", r=r)]
#             haha = List(filters_notin).reduce(func=lambda x, y: x + y)
#             raw = raw + haha  # type: ignore
#         processed = []
#         for item in raw:
#             item_ = PathReduced(item)
#             if all([afilter(item_) for afilter in filters_total]):
#                 processed.append(item_)
#         if not win_order: return List(processed)
#         import re
#         processed.sort(key=lambda x: [int(k) if k.isdigit() else k for k in re.split('([0-9]+)', string=x.stem)])
#         return List(processed)

#     def move(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, rel2it: bool = False, overwrite: bool = False, verbose: bool = True, parents: bool = True, content: bool = False) -> 'PathReduced':
#         path = self._resolve_path(folder=folder, name=name, path=path, default_name=self.absolute().name, rel2it=rel2it)
#         if parents: path.parent.create(parents=True, exist_ok=True)
#         slf = self.expanduser().resolve()
#         if content:
#             assert self.is_dir(), NotADirectoryError(f"💥 When `content` flag is set to True, path must be a directory. It is not: `{repr(self)}`")
#             self.search("*").apply(lambda x: x.move(folder=path.parent, content=False, overwrite=overwrite))
#             return path  # contents live within this directory.
#         if overwrite:
#             tmp_path = slf.rename(path.parent.absolute() / randstr())
#             path.delete(sure=True, verbose=verbose)
#             tmp_path.rename(path)  # works if moving a path up and parent has same name
#         else:
#             try:
#                 slf.rename(path)  # self._return(res=path, inplace=True, operation='rename', orig=False, verbose=verbose, strict=True, msg='')
#             except OSError as oe: # OSError: [Errno 18] Invalid cross-device link:
#                 # https://stackoverflow.com/questions/42392600/oserror-errno-18-invalid-cross-device-link
#                 import shutil
#                 shutil.move(str(slf), str(path))
#                 _ = oe
#         if verbose: print(f"🚚 MOVED {repr(self)} ==> {repr(path)}`")
#         return path

#     def copy(self, folder: OPLike = None, name: Optional[str]= None, path: OPLike = None, content: bool = False, verbose: bool = True, append: Optional[str] = None, overwrite: bool = False, orig: bool = False) -> 'PathReduced':
#         dest = self._resolve_path(folder=folder, name=name, path=path, default_name=self.name, rel2it=False)
#         dest = dest.expanduser().resolve().create(parents_only=True)
#         slf = self.expanduser().resolve()
#         if dest == slf:
#             dest = self.append(append if append is not None else f"_copy_{randstr()}")
#         if not content and overwrite and dest.exists(): dest.delete(sure=True)
#         if not content and not overwrite and dest.exists(): raise FileExistsError(f"💥 Destination already exists: {repr(dest)}")
#         if slf.is_file():
#             import shutil
#             shutil.copy(str(slf), str(dest))
#             if verbose: print(f"🖨️ COPIED {repr(slf)} ==> {repr(dest)}")
#         elif slf.is_dir():
#             dest = dest.parent if content else dest
#             # from distutils.dir_util import copy_tree
#             from shutil import copytree
#             copytree(str(slf), str(dest))
#             if verbose: print(f"🖨️ COPIED {'Content of ' if content else ''} {repr(slf)} ==> {repr(dest)}")
#         else: print(f"💥 Could NOT COPY. Not a file nor a path: {repr(slf)}.")
#         return dest if not orig else self

#     def with_name(self, name: str, verbose: bool = True, inplace: bool = False, overwrite: bool = False, **kwargs: Any):
#         return self._return(self.parent / name, verbose=verbose, operation="rename", inplace=inplace, overwrite=overwrite, **kwargs)

#     def symlink_to(self, target: PLike, verbose: bool = True, overwrite: bool = False, orig: bool = False, strict: bool = True):  # pylint: disable=W0237
#         self.parent.create()
#         target_obj = PathReduced(target).expanduser().resolve()
#         if strict: assert target_obj.exists(), f"Target path `{target}` (aka `{target_obj}`) doesn't exist. This will create a broken link."
#         if overwrite and (self.is_symlink() or self.exists()): self.delete(sure=True, verbose=verbose)
#         from platform import system
#         from crocodile.meta import Terminal
#         if system() == "Windows" and not Terminal.is_user_admin():  # you cannot create symlink without priviliages.
#             Terminal.run_as_admin(file=sys.executable, params=f" -c \"from pathlib import Path; Path(r'{self.expanduser()}').symlink_to(r'{str(target_obj)}')\"", wait=True)
#         else: super(PathReduced, self.expanduser()).symlink_to(str(target_obj))
#         return self._return(target_obj, operation='Whack', inplace=False, orig=orig, verbose=verbose, msg=f"LINKED {repr(self)} ➡️ {repr(target_obj)}")

#     @staticmethod
#     def tmp(folder: OPLike = None, file: Optional[str] = None, root: str = "~/tmp_results") -> 'PathReduced':
#         return PathReduced(root).expanduser().joinpath(folder or "").joinpath(file or "").create(parents_only=True if file else False)

#     @staticmethod
#     def tmpfile(name: Optional[str]= None, suffix: str = "", folder: OPLike = None, tstamp: bool = False, noun: bool = False) -> 'PathReduced':
#         name_concrete = name or randstr(noun=noun)
#         return PathReduced.tmp(file=name_concrete + "_" + randstr() + (("_" + str(timestamp())) if tstamp else "") + suffix, folder=folder or "tmp_files")

#     def to_cloud(self, cloud: str, remotepath: OPLike = None, zip: bool = False,encrypt: bool = False,  # pylint: disable=W0621, W0622
#                  key: Optional[bytes] = None, pwd: Optional[str] = None, rel2home: bool = False, strict: bool = True,
#                  obfuscate: bool = False,
#                  share: bool = False, verbose: bool = True, os_specific: bool = False, transfers: int = 10, root: Optional[str] = "myhome") -> 'PathReduced':
#         to_del = []
#         localpath = self.expanduser().absolute() if not self.exists() else self
#         if zip:
#             localpath = localpath.zip(inplace=False)
#             to_del.append(localpath)
#         if encrypt:
#             localpath = localpath.encrypt(key=key, pwd=pwd, inplace=False)
#             to_del.append(localpath)
#         if remotepath is None:
#             rp = localpath.get_remote_path(root=root, os_specific=os_specific, rel2home=rel2home, strict=strict, obfuscate=obfuscate)  # if rel2home else (PathReduced(root) / localpath if root is not None else localpath)
#         else: rp = PathReduced(remotepath)
#         rclone_cmd = f"""rclone copyto '{localpath.as_posix()}' '{cloud}:{rp.as_posix()}' {'--progress' if verbose else ''} --transfers={transfers}"""
#         from crocodile.meta import Terminal
#         if verbose: print(f"{'⬆️'*5} UPLOADING with `{rclone_cmd}`")
#         shell_to_use = "powershell" if sys.platform == "win32" else "bash"
#         res = Terminal(stdout=None if verbose else subprocess.PIPE).run(rclone_cmd, shell=shell_to_use).capture()
#         _ = [item.delete(sure=True) for item in to_del]
#         assert res.is_successful(strict_err=False, strict_returcode=True), res.print(capture=False, desc="Cloud Storage Operation")
#         if verbose: print(f"{'⬆️'*5} UPLOAD COMPLETED.")
#         if share:
#             if verbose: print("🔗 SHARING FILE")
#             shell_to_use = "powershell" if sys.platform == "win32" else "bash"
#             res = Terminal().run(f"""rclone link '{cloud}:{rp.as_posix()}'""", shell=shell_to_use).capture()
#             tmp = res.op2path(strict_err=False, strict_returncode=False)
#             if tmp is None:
#                 res.print()
#                 raise RuntimeError(f"💥 Could not get link for {self}.")
#             else:
#                 res.print_if_unsuccessful(desc="Cloud Storage Operation", strict_err=True, strict_returncode=True)
#             return tmp
#         return self

#     def from_cloud(self, cloud: str, remotepath: OPLike = None, decrypt: bool = False, unzip: bool = False,  # type: ignore  # pylint: disable=W0621
#                    key: Optional[bytes] = None, pwd: Optional[str] = None, rel2home: bool = False, os_specific: bool = False, strict: bool = True,
#                    transfers: int = 10, root: Optional[str] = "myhome", verbose: bool = True, overwrite: bool = True, merge: bool = False,):
#         if remotepath is None:
#             remotepath = self.get_remote_path(root=root, os_specific=os_specific, rel2home=rel2home, strict=strict)
#             remotepath += ".zip" if unzip else ""
#             remotepath += ".enc" if decrypt else ""
#         else: remotepath = PathReduced(remotepath)
#         localpath = self.expanduser().absolute()
#         localpath += ".zip" if unzip else ""
#         localpath += ".enc" if decrypt else ""
#         rclone_cmd = f"""rclone copyto '{cloud}:{remotepath.as_posix()}' '{localpath.as_posix()}' {'--progress' if verbose else ''} --transfers={transfers}"""
#         from crocodile.meta import Terminal
#         if verbose: print(f"{'⬇️' * 5} DOWNLOADING with `{rclone_cmd}`")
#         shell_to_use = "powershell" if sys.platform == "win32" else "bash"
#         res = Terminal(stdout=None if verbose else subprocess.PIPE).run(rclone_cmd, shell=shell_to_use)
#         success = res.is_successful(strict_err=False, strict_returcode=True)
#         if not success:
#             res.print(capture=False, desc="Cloud Storage Operation")
#             return None
#         if decrypt: localpath = localpath.decrypt(key=key, pwd=pwd, inplace=True)
#         if unzip: localpath = localpath.unzip(inplace=True, verbose=True, overwrite=overwrite, content=True, merge=merge)
#         return localpath

#     # ============= Internal Helper Methods ==================

#     def _return(self, res: 'PathReduced', operation: Literal['rename', 'delete', 'Whack'], inplace: bool = False, overwrite: bool = False, orig: bool = False, verbose: bool = False, strict: bool = True, msg: str = "", __delayed_msg__: str = "") -> 'PathReduced':
#         if inplace:
#             assert self.exists(), f"`inplace` flag is only relevant if the path exists. It doesn't {self}"
#             if operation == "rename":
#                 if overwrite and res.exists(): res.delete(sure=True, verbose=verbose)
#                 if not overwrite and res.exists():
#                     if strict: raise FileExistsError(f"❌ RENAMING failed. File `{res}` already exists.")
#                     else:
#                         if verbose: print(f"⚠️ SKIPPED RENAMING {repr(self)} ➡️ {repr(res)} because FileExistsError and scrict=False policy.")
#                         return self if orig else res
#                 self.rename(res)
#                 msg = msg or f"RENAMED {repr(self)} ➡️ {repr(res)}"
#             elif operation == "delete":
#                 self.delete(sure=True, verbose=False)
#                 __delayed_msg__ = f"DELETED 🗑️❌ {repr(self)}."
#         if verbose and msg != "":
#             try: print(msg)  # emojie print error.
#             except UnicodeEncodeError: print("PathReduced._return warning: UnicodeEncodeError, could not print message.")
#         if verbose and __delayed_msg__ != "":
#             try: print(__delayed_msg__)
#             except UnicodeEncodeError: print("PathReduced._return warning: UnicodeEncodeError, could not print message.")
#         return self if orig else res

#     def _resolve_path(self, folder: OPLike, name: Optional[str], path: OPLike, default_name: str, rel2it: bool = False) -> 'PathReduced':
#         """:param rel2it: `folder` or `path` are relative to `self` as opposed to cwd. This is used when resolving '../dir'"""
#         if path is not None:
#             path = PathReduced(self.joinpath(path).resolve() if rel2it else path).expanduser().resolve()
#             assert folder is None and name is None, "If `path` is passed, `folder` and `name` cannot be passed."
#             assert not path.is_dir(), f"`path` passed is a directory! it must not be that. If this is meant, pass it with `folder` kwarg. `{path}`"
#             return path
#         name, folder = (default_name if name is None else str(name)), (self.parent if folder is None else folder)  # good for edge cases of path with single part.  # means same directory, just different name
#         return PathReduced(self.joinpath(folder).resolve() if rel2it else folder).expanduser().resolve() / name

#     def create(self, parents: bool = True, exist_ok: bool = True, parents_only: bool = False) -> 'PathReduced':
#         target_path = self.parent if parents_only else self
#         target_path.mkdir(parents=parents, exist_ok=exist_ok)
#         return self

#     def append(self, name: str = '', index: bool = False, suffix: Optional[str] = None, verbose: bool = True, **kwargs: Any) -> 'PathReduced':
#         """Returns a new path object with the name appended to the stem of the path. If `index` is True, the name will be the index of the path in the parent directory."""
#         if index:
#             appended_name = f'{name}_{len(self.parent.search(f"*{self.trunk}*"))}'
#             return self.append(name=appended_name, index=False, verbose=verbose, suffix=suffix, **kwargs)
#         full_name = (name or ("_" + str(timestamp())))
#         full_suffix = suffix or ''.join(('bruh' + self).suffixes)
#         subpath = self.trunk + full_name + full_suffix
#         return self._return(self.parent.joinpath(subpath), operation="rename", verbose=verbose, **kwargs)

#     @property
#     def trunk(self) -> str: 
#         return self.name.split('.')[0]  # """ useful if you have multiple dots in file path where `.stem` fails."""

#     def as_zip_path(self):
#         import zipfile
#         res = self.expanduser().resolve()
#         return zipfile.Path(res)

#     def to_str(self) -> str: 
#         return str(self)

#     def get_remote_path(self, root: Optional[str], os_specific: bool = False, rel2home: bool = True, strict: bool = True, obfuscate: bool = False) -> 'PathReduced':
#         import platform
#         tmp1: str = (platform.system().lower() if os_specific else 'generic_os')
#         if not rel2home: path = self
#         else:
#             try: path = self.rel2home()
#             except ValueError as ve:
#                 if strict: raise ve
#                 path = self
#         if obfuscate:
#             from crocodile.msc.obfuscater import obfuscate as obfuscate_func
#             name = obfuscate_func(seed=PathReduced.home().joinpath('dotfiles/creds/data/obfuscation_seed').read_text().rstrip(), data=path.name)
#             path = path.with_name(name=name)
#         if isinstance(root, str):  # the following is to avoid the confusing behaviour of A.joinpath(B) if B is absolute.
#             part1 = path.parts[0]
#             if part1 == "/": sanitized_path = path[1:].as_posix()
#             else: sanitized_path = path.as_posix()
#             return PathReduced(root + "/" + tmp1 + "/" + sanitized_path)
#         return tmp1 / path

#     def rel2home(self, ) -> 'PathReduced': 
#         return self._return(PathReduced(self.expanduser().absolute().relative_to(Path.home())), operation='Whack')  # very similat to collapseuser but without "~" being added so its consistent with rel2cwd.

#     # ============= Path object overrides ==================
    
#     def __getitem__(self, slici: Union[int, list[int], slice]):
#         if isinstance(slici, list): return PathReduced(*[self[item] for item in slici])
#         elif isinstance(slici, int): return PathReduced(self.parts[slici])
#         return PathReduced(*self.parts[slici])  # must be a slice

#     def __add__(self, other: PLike) -> 'PathReduced':
#         return self.parent.joinpath(self.name + str(other))  # used append and prepend if the addition wanted to be before suffix.

#     def __radd__(self, other: PLike) -> 'PathReduced':
#         return self.parent.joinpath(str(other) + self.name)  # other + PathReduced and `other` doesn't know how to make this addition.

#     def __sub__(self, other: PLike) -> 'PathReduced':
#         res = PathReduced(str(self).replace(str(other), ""))
#         return (res[1:] if str(res[0]) in {"\\", "/"} else res) if len(res) else res  # paths starting with "/" are problematic. e.g ~ / "/path" doesn't work.

#     def __truediv__(self, other):
#         return PathReduced(super().__truediv__(other))

#     def joinpath(self, *args):
#         return PathReduced(super().joinpath(*args))

#     def parent(self):
#         return PathReduced(super().parent)

#     def resolve(self, strict: bool = False):
#         try: 
#             return PathReduced(super().resolve(strict=strict))
#         except OSError: 
#             return self

#     def expanduser(self):
#         return PathReduced(super().expanduser())

#     def absolute(self):
#         return PathReduced(super().absolute())

#     def rename(self, target):
#         return PathReduced(super().rename(target))

#     # ============= Missing methods that might be needed ==================
    
#     # These methods are referenced in the cloud methods but might not be implemented
#     # Adding stubs to prevent errors
    
#     def zip(self, inplace: bool = False, **kwargs):
#         # Stub - would need full implementation from original class
#         raise NotImplementedError("zip method not implemented in PathReduced")
    
#     def encrypt(self, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, **kwargs):
#         # Stub - would need full implementation from original class  
#         raise NotImplementedError("encrypt method not implemented in PathReduced")
    
#     def decrypt(self, key: Optional[bytes] = None, pwd: Optional[str] = None, inplace: bool = False, **kwargs):
#         # Stub - would need full implementation from original class
#         raise NotImplementedError("decrypt method not implemented in PathReduced")
    
#     def unzip(self, inplace: bool = False, **kwargs):
#         # Stub - would need full implementation from original class
#         raise NotImplementedError("unzip method not implemented in PathReduced")
