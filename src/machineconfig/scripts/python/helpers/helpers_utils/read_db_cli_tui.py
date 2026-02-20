
from typing import Optional, Literal, TypeAlias
from pathlib import Path
import glob as glob_module

BACKEND_LOOSE: TypeAlias = Literal[
    "rainfrog", "r",
    "lazysql", "l",
    "dblab", "d",
    "usql", "u",
    "harlequin", "h",
    "sqlit", "s"
]
BACKEND: TypeAlias = Literal[
    "rainfrog",
    "lazysql",
    "dblab",
    "usql",
    "harlequin",
    "sqlit"
]
LOOSE2STRICT: dict[BACKEND_LOOSE, BACKEND] = {
    "rainfrog": "rainfrog", "r": "rainfrog",
    "lazysql": "lazysql",   "l": "lazysql",
    "dblab": "dblab",       "d": "dblab",
    "usql": "usql",         "u": "usql",
    "harlequin": "harlequin", "h": "harlequin",
    "sqlit": "sqlit",       "s": "sqlit",
}

# harlequin is the only backend that can open multiple DB files simultaneously
MULTI_DB_CAPABLE: frozenset[BACKEND] = frozenset({"harlequin"})
# backends that can natively handle duckdb connection strings
DUCKDB_CAPABLE: frozenset[BACKEND] = frozenset({"harlequin", "usql"})

DUCKDB_EXTS: frozenset[str] = frozenset({".duckdb", ".ddb"})
EXT_TO_PREFIX: dict[str, str] = {
    ".duckdb": "duckdb://", ".ddb": "duckdb://",
    ".sqlite": "sqlite://", ".sqlite3": "sqlite://", ".db": "sqlite://",
    ".db3": "sqlite://", ".s3db": "sqlite://", ".sl3": "sqlite://",
    ".postgres": "postgres://", ".pg": "postgres://", ".postgresql": "postgres://",
    ".mysql": "mysql://",
}


def _find_files(pattern: str, root: Path, recursive: bool) -> list[Path]:
    glob_base = str(root / "**" / pattern) if recursive else str(root / pattern)
    return sorted(Path(p).resolve() for p in glob_module.glob(glob_base, recursive=recursive))


def _url_for(p: Path) -> str:
    prefix = EXT_TO_PREFIX.get(p.suffix.lower(), "sqlite://")
    return f'"{prefix}{p}"'


def _validate_backend(backend: BACKEND, resolved: list[Path]) -> None:
    is_all_duckdb = all(p.suffix.lower() in DUCKDB_EXTS for p in resolved)
    if is_all_duckdb and backend not in DUCKDB_CAPABLE:
        duckdb_capable_list = ", ".join(sorted(DUCKDB_CAPABLE))
        raise ValueError(
            f"Backend '{backend}' does not support DuckDB files.\n"
            f"DuckDB-capable backends: {duckdb_capable_list}\n"
            f"Files: {[str(p) for p in resolved]}"
        )
    if len(resolved) > 1 and backend not in MULTI_DB_CAPABLE:
        multi_capable_list = ", ".join(sorted(MULTI_DB_CAPABLE))
        raise ValueError(
            f"Backend '{backend}' cannot open multiple files simultaneously.\n"
            f"Multi-file-capable backends: {multi_capable_list}\n"
            f"Files ({len(resolved)}): {[str(p) for p in resolved]}"
        )


def app(
    path: Optional[str] = None,
    find: Optional[str] = None,
    find_root: Optional[str] = None,
    recursive: bool = False,
    backend: BACKEND_LOOSE = "harlequin",
    read_only: bool = False,
    theme: Optional[str] = None,
    limit: Optional[int] = None,
) -> None:
    """🗃️ TUI DB Visualizer.

    path       – explicit file path (single DB).
    find       – glob pattern to discover DB files, e.g. '*.duckdb' or '**/*.duckdb'.
    find_root  – root directory for `find` (default: current working directory).
    recursive  – search subdirectories when using `find`.
    """
    backend_strict = LOOSE2STRICT[backend]
    from machineconfig.utils.code import exit_then_run_shell_script

    resolved: list[Path] = []
    if path is not None and find is not None:
        raise ValueError("Provide either `path` or `find`, not both.")
    if path is not None:
        resolved = [Path(path).expanduser().resolve()]
    elif find is not None:
        root = Path(find_root).expanduser().resolve() if find_root is not None else Path.cwd()
        resolved = _find_files(find, root, recursive)
        if not resolved:
            raise FileNotFoundError(f"No files matched pattern '{find}' under '{root}' (recursive={recursive})")
        print(f"Found {len(resolved)} file(s) matching '{find}' under '{root}'")

    if resolved:
        _validate_backend(backend_strict, resolved)

    shell_script_init = 'echo "Initializing TUI DB Visualizer..."'
    cmd = ""
    match backend_strict:
        case "rainfrog":
            cmd = "rainfrog"
            if resolved:
                cmd += f" --url {_url_for(resolved[0])}"
        case "lazysql":
            cmd = "lazysql"
            if read_only:
                cmd += " -read-only"
            if resolved:
                cmd += f" {_url_for(resolved[0])}"
        case "dblab":
            cmd = "dblab"
            if limit is not None:
                cmd += f" --limit {limit}"
            if resolved:
                cmd += f" --url {_url_for(resolved[0])}"
        case "usql":
            cmd = "usql"
            if resolved:
                cmd += f" {_url_for(resolved[0])}"
        case "harlequin":
            cmd = "harlequin"
            if read_only:
                cmd += " --read-only"
            if theme:
                cmd += f" --theme {theme}"
            if limit is not None:
                cmd += f" --limit {limit}"
            for p in resolved:
                cmd += f' "{p}"'
        case "sqlit":
            cmd = "sqlit"
            if theme:
                cmd += f" --theme {theme}"
            if limit is not None:
                cmd += f" --max-rows {limit}"
            if resolved:
                cmd += f" {_url_for(resolved[0])}"

    shell_script = f"{shell_script_init}\n{cmd}"
    exit_then_run_shell_script(shell_script)
