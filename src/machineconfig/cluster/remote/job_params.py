from typing import Callable
from dataclasses import dataclass
from pathlib import Path

from machineconfig.cluster.remote.models import WorkloadParams


@dataclass
class JobParams:
    description: str
    ssh_repr: str
    ssh_repr_remote: str
    error_message: str
    session_name: str
    tab_name: str
    file_manager_path: str
    repo_path_rh: str
    file_path_rh: str
    file_path_r: str
    func_module: str
    func_class: str | None
    func_name: str | None

    def to_dict(self) -> dict[str, object]:
        return {k: v for k, v in self.__dict__.items()}

    @staticmethod
    def from_dict(d: dict[str, object]) -> "JobParams":
        return JobParams(
            description=str(d.get("description", "")), ssh_repr=str(d.get("ssh_repr", "")), ssh_repr_remote=str(d.get("ssh_repr_remote", "")),
            error_message=str(d.get("error_message", "")), session_name=str(d.get("session_name", "")), tab_name=str(d.get("tab_name", "")),
            file_manager_path=str(d.get("file_manager_path", "")), repo_path_rh=str(d.get("repo_path_rh", "")),
            file_path_rh=str(d.get("file_path_rh", "")), file_path_r=str(d.get("file_path_r", "")), func_module=str(d.get("func_module", "")),
            func_class=str(d["func_class"]) if d.get("func_class") else None, func_name=str(d["func_name"]) if d.get("func_name") else None,
        )

    @staticmethod
    def empty() -> "JobParams":
        return JobParams(repo_path_rh="", file_path_rh="", file_path_r="", func_module="", func_class=None, func_name=None, description="", ssh_repr="", ssh_repr_remote="", error_message="", session_name="", tab_name="", file_manager_path="")

    @staticmethod
    def from_callable(func: Callable[..., object]) -> "JobParams":
        func_name = func.__name__
        func_module = func.__module__
        if func_module == "<run_path>":
            func_module = Path(func.__globals__["__file__"]).name
        if func_module == "__main__":
            raise ValueError(f"Function must be defined in a module, not __main__. Import `{func_name}` from its module.")
        func_file = Path(func.__code__.co_filename)
        func_class = func.__qualname__.split(".")[0] if func.__name__ != func.__qualname__ else None
        repo_path, func_relative_file = _resolve_repo_path(func_file)
        return JobParams(
            repo_path_rh=_collapse_user(repo_path), file_path_rh=_collapse_user(repo_path / func_relative_file),
            file_path_r=str(func_relative_file), func_module=func_module, func_class=func_class, func_name=func_name,
            description="", ssh_repr="", ssh_repr_remote="", error_message="", session_name="", tab_name="", file_manager_path="",
        )

    @staticmethod
    def from_script(script_path: str | Path) -> "JobParams":
        func_file = Path(script_path)
        repo_path, func_relative_file = _resolve_repo_path(func_file)
        return JobParams(
            repo_path_rh=_collapse_user(repo_path), file_path_rh=_collapse_user(repo_path / func_relative_file),
            file_path_r=str(func_relative_file), func_module=func_file.stem, func_class=None, func_name=None,
            description="", ssh_repr="", ssh_repr_remote="", error_message="", session_name="", tab_name="", file_manager_path="",
        )

    def get_execution_line(self, workload_params: WorkloadParams | None, parallelize: bool, wrap_in_try_except: bool) -> str:
        lines: list[str] = []
        if workload_params is not None:
            lines.append(f"workload_params = WorkloadParams(**{workload_params.__dict__})")
            lines.append(f"repo_path = Path(r'{self.repo_path_rh}').expanduser().resolve()")
            lines.append(f"file_root = Path(r'{self.file_path_rh}').expanduser().resolve().parent")
            lines.append("import sys")
            lines.append("sys.path.insert(0, str(repo_path))")
            lines.append("sys.path.insert(0, str(file_root))")

        if self.func_name is not None:
            module_name = self.func_module.removesuffix(".py")
            if self.func_class is None:
                lines.append(f"from {module_name} import {self.func_name} as func")
            else:
                lines.append(f"from {module_name} import {self.func_class}")
                lines.append(f"func = {self.func_class}.{self.func_name}")
        else:
            lines.append("res = None")
            lines.append(f"exec(Path(r'{self.file_path_rh}').expanduser().read_text(encoding='utf-8'))")
            return "\n".join(lines)

        if workload_params is not None and not parallelize:
            lines.append("res = func(workload_params=workload_params, **func_kwargs)")
        elif workload_params is not None and parallelize:
            split_dicts = [item.__dict__ for item in workload_params.split_to_jobs(jobs=workload_params.jobs)]
            lines.append(f"kwargs_workload = {split_dicts}")
            lines.append("from concurrent.futures import ProcessPoolExecutor")
            lines.append("split_params = [WorkloadParams(**kw) for kw in kwargs_workload]")
            lines.append("with ProcessPoolExecutor(max_workers={}) as pool:".format(workload_params.jobs))
            lines.append("    futures = [pool.submit(func, workload_params=wp, **func_kwargs) for wp in split_params]")
            lines.append("    res = [f.result() for f in futures]")
        else:
            lines.append("res = func(**func_kwargs)")

        if wrap_in_try_except:
            import textwrap
            body = textwrap.indent("\n".join(lines), "    ")
            return f"try:\n{body}\nexcept Exception as e:\n    print(e)\n    params.error_message = str(e)\n    res = None"
        return "\n".join(lines)

    def is_installable(self) -> bool:
        return (Path(self.repo_path_rh).expanduser() / "setup.py").exists()


def _resolve_repo_path(func_file: Path) -> tuple[Path, Path]:
    try:
        import git
        repo = git.Repo(str(func_file), search_parent_directories=True)
        repo_path = Path(str(repo.working_dir))
        func_relative_file = func_file.resolve().relative_to(repo_path.resolve())
    except Exception:
        repo_path = func_file.parent
        func_relative_file = Path(func_file.name)
    return repo_path, func_relative_file


def _collapse_user(p: Path) -> str:
    try:
        return "~/" + str(p.expanduser().resolve().relative_to(Path.home()))
    except ValueError:
        return str(p)
