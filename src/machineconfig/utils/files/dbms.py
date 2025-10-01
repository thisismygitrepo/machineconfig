import time
from typing import Optional, Any, Callable

import polars as pl

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text, inspect as inspect__
from sqlalchemy.engine import Engine, Connection, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Inspector
from sqlalchemy.sql.schema import MetaData
from pathlib import Path as P

OPLike = Optional[P] | str | None


class DBMS:
    def __init__(self, engine: Engine, sch: Optional[str] = None, vws: bool = False):
        self.eng: Engine = engine
        self.con: Optional[Connection] = None
        self.ses: Optional[Session] = None
        self.insp: Optional[Inspector] = None
        self.meta: Optional[MetaData] = None
        db_path = P(self.eng.url.database) if self.eng.url.database else None
        if db_path and db_path.exists():
            self.path: Optional[P] = db_path
        else: self.path = None

        # self.db = db
        self.sch = sch
        self.vws: bool = vws
        self.schema: list[str] = []

        self.sch_tab: dict[str, list[str]]
        self.sch_vws: dict[str, list[str]]
        self.description: Optional[pl.DataFrame] = None
        # self.tables = None
        # self.views = None
        # self.sch_tab: Optional[Struct] = None
        # self.sch_vws: Optional[Struct] = None
        # if inspect: self.refresh()
        # self.ip_formatter: Optional[Any] = None
        # self.db_specs: Optional[Any] = None
        if self.path is not None:
            if self.path.is_file():
                path_repr = self.path.as_uri()
            else:
                path_repr = self.path
            print(f"Database at {path_repr} is ready.")

    def refresh(self, sch: Optional[str] = None) -> 'DBMS':  # fails if multiple schemas are there and None is specified
        self.con = self.eng.connect()
        self.ses = sessionmaker()(bind=self.eng)  # ORM style
        self.meta = MetaData()
        self.meta.reflect(bind=self.eng, schema=sch or self.sch)
        insp = inspect__(subject=self.eng)
        self.insp = insp
        assert self.insp is not None
        self.schema = self.insp.get_schema_names()
        print(f"Inspecting tables of schema `{self.schema}` {self.eng}")
        self.sch_tab = {k: v for k, v in zip(self.schema, [insp.get_table_names(schema=x) for x in self.schema])}  # dict(zip(self.schema, self.schema.apply(lambda x: self.insp.get_table_names(schema=x))))  #
        print(f"Inspecting views of schema `{self.schema}` {self.eng}")
        self.sch_vws = {k: v for k, v in zip(self.schema, [insp.get_view_names(schema=x) for x in self.schema])}
        return self

    @classmethod
    def from_local_db(cls, path: OPLike = None, echo: bool = False, share_across_threads: bool = False, pool_size: int = 5, **kwargs: Any):
        return cls(engine=cls.make_sql_engine(path=path, echo=echo, share_across_threads=share_across_threads, pool_size=pool_size, **kwargs))

    def __repr__(self): return f"DataBase @ {self.eng}"
    def get_columns(self, table: str, sch: Optional[str] = None):
        assert self.meta is not None
        return self.meta.tables[self._get_table_identifier(table=table, sch=sch)].exported_columns.keys()
    def close(self, sleep: int = 2):
        if self.path:
            print(f"Terminating database `{self.path.as_uri() if self.path.is_file() and 'memory' not in str(self.path) else self.path}`")
        if self.con: self.con.close()
        if self.ses: self.ses.close()
        self.eng.pool.dispose()
        self.eng.dispose()
        time.sleep(sleep)
    def _get_table_identifier(self, table: str, sch: Optional[str]):
        if sch is None: sch = self.sch
        if sch is not None:
            # Handle DuckDB schema names that contain dots (e.g., "klines.main")
            if self.eng.url.drivername == 'duckdb' and '.' in sch and sch.endswith('.main'):
                # For DuckDB schemas like "klines.main", just use the table name without schema
                return f'"{table}"'
            else:
                return f'"{sch}"."{table}"'
        else:
            return f'"{table}"'

    @staticmethod
    def make_sql_engine(path: OPLike = None, echo: bool = False, dialect: str = "sqlite", driver: str = ["pysqlite", "DBAPI"][0], pool_size: int = 5, share_across_threads: bool = True, **kwargs: Any):
        """Establish lazy initialization with database"""
        from sqlalchemy.pool import StaticPool, NullPool
        _ = NullPool
        _ = driver
        if str(path) == "memory":
            print("Linking to in-memory database.")
            if share_across_threads:
                # see: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
                return create_engine(url=f"{dialect}+{driver}:///:memory:", echo=echo, future=True, poolclass=StaticPool, connect_args={"check_same_thread": False})
            else:
                return create_engine(url=f"{dialect}+{driver}:///:memory:", echo=echo, future=True, pool_size=pool_size, **kwargs)
        if path is None:
            tmp_dir = P.home().joinpath(".tmp").joinpath("tmp_dbs")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".sqlite", dir=str(tmp_dir), delete=False) as tmp_file:
                path = P(tmp_file.name)
        else:
            path = P(path).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
        path_repr = path.as_uri() if path.is_file() else path
        dialect = path.suffix.removeprefix('.')
        print(f"Linking to database at {path_repr}")
        connect_args = kwargs.pop("connect_args", {}) or {}
        try:
            if path.suffix == ".duckdb":  # only apply for duckdb files
                # don't overwrite user's explicit setting if already provided
                connect_args.setdefault("read_only", True)
                print(" - Opening DuckDB in read-only mode.")
        except Exception:
            pass
        if pool_size == 0:
            res = create_engine(url=f"{dialect}:///{path}", echo=echo, future=True, poolclass=NullPool, connect_args=connect_args, **kwargs)  # echo flag is just a short for the more formal way of logging sql commands.
        else:
            res = create_engine(url=f"{dialect}:///{path}", echo=echo, future=True, pool_size=pool_size, connect_args=connect_args, **kwargs)  # echo flag is just a short for the more formal way of logging sql commands.
        return res
    @staticmethod
    def make_sql_async_engine(path: OPLike = None, echo: bool = False, dialect: str = "sqlite", driver: str = "aiosqlite", pool_size: int = 5, share_across_threads: bool = True, **kwargs: Any):
        """Establish lazy initialization with database"""
        from sqlalchemy.pool import StaticPool, NullPool
        _ = NullPool
        if str(path) == "memory":
            print("Linking to in-memory database.")
            if share_across_threads:
                # see: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
                return create_async_engine(url=f"{dialect}+{driver}://", echo=echo, future=True, poolclass=StaticPool, connect_args={"mode": "memory", "cache": "shared"})
            else:
                return create_async_engine(url=f"{dialect}+{driver}:///:memory:", echo=echo, future=True, pool_size=pool_size, **kwargs)
        if path is None:
            tmp_dir = P.home().joinpath(".tmp").joinpath("tmp_dbs")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".sqlite", dir=str(tmp_dir), delete=False) as tmp_file:
                path = P(tmp_file.name)
        else:
            path = P(path).expanduser().resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
        path_repr = path.as_uri() if path.is_file() else path
        dialect = path.suffix.removeprefix('.')
        print(f"Linking to database at {path_repr}")
        # Add DuckDB-specific read-only flag automatically when pointing to an existing .duckdb file
        connect_args = kwargs.pop("connect_args", {}) or {}
        try:
            if path.suffix == ".duckdb":  # only apply for duckdb files
                # don't overwrite user's explicit setting if already provided
                connect_args.setdefault("read_only", True)
                print(" - Opening DuckDB in read-only mode.")
        except Exception:
            pass
        if pool_size == 0:
            res = create_async_engine(url=f"{dialect}+{driver}:///{path}", echo=echo, future=True, poolclass=NullPool, connect_args=connect_args, **kwargs)  # echo flag is just a short for the more formal way of logging sql commands.
        else:
            res = create_async_engine(url=f"{dialect}+{driver}:///{path}", echo=echo, future=True, pool_size=pool_size, connect_args=connect_args, **kwargs)  # echo flag is just a short for the more formal way of logging sql commands.
        return res

    # ==================== QUERIES =====================================
    def execute_as_you_go(self, *commands: str, res_func: Callable[[Any], Any] = lambda x: x.all(), df: bool = False):
        with self.eng.begin() as conn:
            result = None
            for command in commands:
                result = conn.execute(text(command))
            # conn.commit()  # if driver is sqlite3, the connection is autocommitting. # this commit is only needed in case of DBAPI driver.
            return res_func(result) if not df else pl.DataFrame(res_func(result))

    def execute_begin_once(self, command: str, res_func: Callable[[Any], Any] = lambda x: x.all(), df: bool = False):
        with self.eng.begin() as conn:
            result = conn.execute(text(command))  # no need for commit regardless of driver
            result = res_func(result)
        return result if not df else pl.DataFrame(result)

    def execute(self, command: str):
        with self.eng.begin() as conn:
            result = conn.execute(text(command))
            # conn.commit()
        return result

    # def execute_script(self, command: str, df: bool = False):
    #     with self.eng.begin() as conn: result = conn.executescript(text(command))
    #     return result if not df else pl.DataFrame(result)

    # ========================== TABLES =====================================
    def read_table(self, table: Optional[str] = None, sch: Optional[str] = None, size: int = 5):
        if sch is None:
            # First try to find schemas that have tables (excluding system schemas)
            schemas_with_tables = []
            for schema_name in self.schema:
                if schema_name not in ["information_schema", "pg_catalog", "system"]:
                    if schema_name in self.sch_tab and len(self.sch_tab[schema_name]) > 0:
                        schemas_with_tables.append(schema_name)

            if len(schemas_with_tables) == 0:
                raise ValueError(f"No schemas with tables found. Available schemas: {self.schema}")

            # Prefer non-"main" schemas if available, otherwise use main
            if len(schemas_with_tables) > 1 and "main" in schemas_with_tables:
                sch = [s for s in schemas_with_tables if s != "main"][0]
            else:
                sch = schemas_with_tables[0]
            print(f"Auto-selected schema: `{sch}` from available schemas: {schemas_with_tables}")

        if table is None:
            if sch not in self.sch_tab:
                raise ValueError(f"Schema `{sch}` not found. Available schemas: {list(self.sch_tab.keys())}")
            tables = self.sch_tab[sch]
            assert len(tables) > 0, f"No tables found in schema `{sch}`"
            import random
            table = random.choice(tables)
            print(f"Reading table `{table}` from schema `{sch}`")
        if self.con:
            try:
                res = self.con.execute(text(f'''SELECT * FROM {self._get_table_identifier(table, sch)} '''))
                return pl.DataFrame(res.fetchmany(size))
            except Exception:
                print(f"Error executing query for table `{table}` in schema `{sch}`")
                print(f"Available schemas and tables: {self.sch_tab}")
                raise

    def insert_dicts(self, table: str, *mydicts: dict[str, Any]) -> None:
        cmd = f"""INSERT INTO {table} VALUES """
        for mydict in mydicts: cmd += f"""({tuple(mydict)}), """
        self.execute_begin_once(cmd)

    def describe_db(self):
        self.refresh()
        assert self.meta is not None
        res_all = []
        assert self.ses is not None
        from rich.progress import Progress
        with Progress() as progress:
            task = progress.add_task("Inspecting tables", total=len(self.meta.sorted_tables))
            for tbl in self.meta.sorted_tables:
                table = tbl.name
                if self.sch is not None:
                    table = f"{self.sch}.{table}"
                count = self.ses.query(tbl).count()
                res = dict(table=table, count=count, size_mb=count * len(tbl.exported_columns) * 10 / 1e6,
                           columns=len(tbl.exported_columns), schema=self.sch)
                res_all.append(res)
                progress.update(task, advance=1)
        self.description = pl.DataFrame(res_all)
        return self.description

    def describe_table(self, table: str, sch: Optional[str] = None, dtype: bool = True) -> None:
        print(table.center(100, "="))
        self.refresh()
        assert self.meta is not None
        tbl = self.meta.tables[table]
        assert self.ses is not None
        count = self.ses.query(tbl).count()
        res = dict(name=table, count=count, size_mb=count * len(tbl.exported_columns) * 10 / 1e6)
        from machineconfig.utils.accessories import pprint
        pprint(res, title="TABLE DETAILS")
        dat = self.read_table(table=table, sch=sch, size=2)
        df = dat  # dat is already a polars DataFrame
        print("SAMPLE:\n", df)
        assert self.insp is not None
        if dtype: print("\nDETAILED COLUMNS:\n", pl.DataFrame(self.insp.get_columns(table)))
        print("\n" * 3)


DB_TMP_PATH = P.home().joinpath(".tmp").joinpath("tmp_dbs").joinpath("results").joinpath("data.sqlite")


def to_db(table: str, idx: int, idx_max: int, data: Any):
    import pickle
    DB_TMP_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = DBMS.from_local_db(DB_TMP_PATH)
    time_now = time.time_ns()
    data_blob = pickle.dumps(data)
    create_table = f"""CREATE TABLE IF NOT EXISTS "{table}" (time INT PRIMARY KEY, idx INT, idx_max INT, data BLOB)"""
    insert_row = f"""INSERT INTO "{table}" (time, idx, idx_max, data) VALUES (:time, :idx, :idx_max, :data)"""
    with db.eng.begin() as conn:
        conn.execute(text(create_table))
        conn.execute(
            text(insert_row),
            {'time': time_now, 'idx': idx, 'idx_max': idx_max, 'data': data_blob}
        )
        # conn.commit()
    db.close()


def from_db(table: str):
    import pickle
    DB_TMP_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = DBMS.from_local_db(DB_TMP_PATH)
    with db.eng.connect() as conn:
        res = conn.execute(text(f"""SELECT * FROM "{table}" """))
        records = res.fetchall()
        df = pl.DataFrame(records, schema=['time', 'idx', 'idx_max', 'data'])
        df = df.with_columns(pl.col('data').map_elements(pickle.loads))
        return df


def get_table_specs(engine: Engine, table_name: str) -> pl.DataFrame:
    inspector = inspect__(engine)
    # Collect table information
    columns_info = [{
        'name': col['name'],
        'type': str(col['type']),
        'nullable': col['nullable'],
        'default': col['default'],
        'autoincrement': col.get('autoincrement'),
        'category': 'column'
    } for col in inspector.get_columns(table_name)]
    # Primary keys
    pk_info = [{
        'name': pk,
        'type': None,
        'nullable': False,
        'default': None,
        'autoincrement': None,
        'category': 'primary_key'
    } for pk in inspector.get_pk_constraint(table_name)['constrained_columns']]
    # Foreign keys
    fk_info = [{
        'name': fk['constrained_columns'][0],
        'type': f"FK -> {fk['referred_table']}.{fk['referred_columns'][0]}",
        'nullable': None,
        'default': None,
        'autoincrement': None,
        'category': 'foreign_key'
    } for fk in inspector.get_foreign_keys(table_name)]
    # Indexe
    index_info = [{
        'name': idx['name'],
        'type': f"Index on {', '.join(col for col in idx['column_names'] if col)}",
        'nullable': None,
        'default': None,
        'autoincrement': None,
        'category': 'index',
        'unique': idx['unique']
    } for idx in inspector.get_indexes(table_name)]
    # Combine all information
    all_info = columns_info + pk_info + fk_info + index_info
    # Convert to DataFrame
    df = pl.DataFrame(all_info)
    return df

if __name__ == '__main__':
    pass
