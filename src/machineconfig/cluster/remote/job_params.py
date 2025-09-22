# import git

# from typing import Optional, Callable, Union, Any
# from machineconfig.cluster.remote_machine import WorkloadParams
# from dataclasses import dataclass
# import getpass
# import platform
# # from machineconfig.utils.utils2 import pprint


# @dataclass
# class JobParams:
#     """What Python script needs to run the job. This will be dynamically injected into the script. Notice that all attrs are either strings or integers."""
#     description: str
#     ssh_repr: str
#     ssh_repr_remote: str
#     error_message: str
#     session_name: str
#     tab_name: str
#     file_manager_path: str

#     repo_path_rh: str
#     file_path_rh: str
#     file_path_r: str
#     func_module: str
#     func_class: Optional[str] = None  # the callable might be a function on its own, not a method of a class.
#     func_name: Optional[str] = None  # the job might be running a script as is, no particular method.

#     def auto_commit(self):
#         from git.repo import Repo
#         repo = Repo(PathExtended(self.repo_path_rh).expanduser(), search_parent_directories=True)
#         # do a commit if the repo is dirty
#         if repo.is_dirty():
#             repo.git.add(update=True)
#             repo.index.commit(f"CloudManager auto commit by {getpass.getuser()}@{platform.node()}")
#             print(f"⚠️ Repo {repo.working_dir} was dirty, auto-committed.")
#         else: print(f"✅ Repo {repo.working_dir} was clean, no auto-commit.")

#     def is_installabe(self) -> bool: return True if "setup.py" in PathExtended(self.repo_path_rh).expanduser().absolute().listdir().apply(str) else False
#     @staticmethod
#     def from_empty() -> 'JobParams':
#         return JobParams(repo_path_rh="", file_path_rh="", file_path_r="", func_module="", func_class="", func_name="", description="", ssh_repr="", ssh_repr_remote="", error_message="", session_name="", tab_name="", file_manager_path="")
#     @staticmethod
#     def from_func(func: Union[Callable[[Any], Any], P, str]) -> 'JobParams':
#         # if callable(self.func): executed_obj = f"""**{self.func.__name__}** from *{P(self.func.__code__.co_filename).collapseuser().as_posix()}*"""  # for email.
#         if callable(func) and not isinstance(func, P):
#             func_name = func.__name__
#             func_module = func.__module__
#             if func_module == "<run_path>":  # function imported through readpy module.
#                 func_module = PathExtended(func.__globals__['__file__']).name
#             assert func_module != "__main__", f"Function must be defined in a module, not in __main__. Consider importing `{func.__name__}` or, restart this session and import the contents of this module."
#             if func.__name__ != func.__qualname__:
#                 # print(f"Passed function {func} is a method of a class.")
#                 func_file, func_class = PathExtended(func.__code__.co_filename), func.__qualname__.split(".")[0]
#             else:
#                 # print(f"Passed function {func} is not a method of a class.")
#                 func_file, func_class = PathExtended(func.__code__.co_filename), None
#         elif type(func) is str or type(func) is P:
#             func_file = PathExtended(func)
#             # func = None
#             func_class = None
#             func_name = None
#             func_module = func_file.stem
#         else: raise TypeError(f"Passed function {func} is not a callable or a path to a python file.")
#         try:
#             repo_path = PathExtended(git.Repo(func_file, search_parent_directories=True).working_dir)
#             func_relative_file = func_file.relative_to(repo_path)
#         except Exception as e:
#             print(e)
#             repo_path, func_relative_file = func_file.parent, func_file.name
#         return JobParams(repo_path_rh=repo_path.collapseuser().as_posix(), file_path_rh=repo_path.collapseuser().joinpath(func_relative_file).collapseuser().as_posix(),
#                          file_path_r=PathExtended(func_relative_file).as_posix(),
#                          func_module=func_module, func_class=func_class, func_name=func_name,
#                          description="", ssh_repr="", ssh_repr_remote="", error_message="",
#                          session_name="", tab_name="", file_manager_path="")

#     def get_execution_line(self, workload_params: Optional[WorkloadParams], parallelize: bool, wrap_in_try_except: bool) -> str:
#         # PathExtended(self.repo_path_rh).name}.{self.file_path_r.replace(".py", '').replace('/', '.')#
#         # if func_module is not None:
#         #     # noinspection PyTypeChecker
#         #     module = __import__(func_module, fromlist=[None])
#         #     exec_obj = module.__dict__[func_name] if not bool(func_class) else getattr(module.__dict__[func_class], func_name)
#         # elif func_name is not None:
#         #     # This approach is not conducive to parallelization since "mymod" is not pickleable.
#         #     module = SourceFileLoader("mymod", PathExtended.home().joinpath(rel_full_path).as_posix()).load_module()  # loading the module assumes its not a script, there should be at least if __name__ == __main__ wrapping any script.
#         #     exec_obj = getattr(module, func_name) if not bool(func_class) else getattr(getattr(module, func_class), func_name)
#         # else:
#         #     module = PathExtended.home().joinpath(rel_full_path).readit()  # uses runpy to read .py files.
#         #     exec_obj = module  # for README.md generation.

#         if workload_params is not None: base = f"""
# workload_params = WorkloadParams(**{workload_params.__dict__})
# repo_path = PathExtended(rf'{self.repo_path_rh}').expanduser().absolute()
# file_root = PathExtended(rf'{self.file_path_rh}').expanduser().absolute().parent
# tb.sys.path.insert(0, repo_path.str)
# tb.sys.path.insert(0, file_root.str)
# """
#         else: base = ""

#         # loading function ===============================================================
#         if self.func_name is not None:
#             if self.func_class is None: base += f"""
# from {self.func_module.replace('.py', '')} import {self.func_name} as func
# """
#             elif self.func_class is not None:  # type: ignore
#                 base += f"""
# from {self.func_module.replace('.py', '')} import {self.func_class} as {self.func_class}
# func = {self.func_class}.{self.func_name}
# """
#         else: base = f"""
# res = None  # in case the file did not define it.
# # --------------------------------- SCRIPT AS IS
# {P(self.file_path_rh).expanduser().read_text(encoding="utf-8")}
# # --------------------------------- END OF SCRIPT AS IS
# """

#         if workload_params is not None and parallelize is False: base += """
# res = func(workload_params=workload_params, **func_kwargs)
# """
#         elif workload_params is not None and parallelize is True: base += f"""
# kwargs_workload = {list([item.__dict__ for item in workload_params.split_to_jobs()])}
# workload_params = []
# for idx, x in enumerate(kwargs_workload):
#             pprint(x, f"Instance {{idx}}")
#     workload_params.append(WorkloadParams(**x))
# print("\n" * 2)
# res = L(workload_params).apply(lambda a_workload_params: func(workload_params=a_workload_params, **func_kwargs), jobs={workload_params.jobs})
# """
#         else: base += """
# res = func(**func_kwargs)
# """

#         if wrap_in_try_except:
#             import textwrap
#             base = textwrap.indent(base, " " * 4)
#             base = f"""
# try:
# {base}
# except Exception as e:
#     print(e)
#     params.error_message = str(e)
#     res = None

# """
#         return base
