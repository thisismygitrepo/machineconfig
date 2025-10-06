import time
from typing import Optional, Any, Callable

import polars as pl

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text, inspect as inspect__
from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import MetaData
from pathlib import Path as P

OPLike = Optional[P] | str | None


class DBMS:
    def __init__(self, engine: Engine):
        self.eng: Engine = engine

    @staticmethod
    def from_local_db(path: OPLike = None, echo: bool = False, share_across_threads: bool = False, pool_size: int = 5, **kwargs: Any):
        return DBMS(engine=DBMS.make_sql_engine(path=path, echo=echo, share_across_threads=share_across_threads, pool_size=pool_size, **kwargs))

    def __repr__(self): return f"DataBase @ {self.eng}"
    def close(self, sleep: int = 2):
        self.eng.pool.dispose()
        self.eng.dispose()
        time.sleep(sleep)
    @staticmethod
    def _get_table_identifier(engine: Engine, table: str, sch: Optional[str]):
        if sch is not None:
            # Handle DuckDB schema names that contain dots (e.g., "klines.main")
            if engine.url.drivername == 'duckdb' and '.' in sch and sch.endswith('.main'):
                # For DuckDB schemas like "klines.main", just use the table name without schema
                return f'"{table}"'
            else:
                return f'"{sch}"."{table}"'
        else:
            return f'"{table}"'

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
    def insert_dicts(self, table: str, *mydicts: dict[str, Any]) -> None:
        cmd = f"""INSERT INTO {table} VALUES """
        for mydict in mydicts: cmd += f"""({tuple(mydict)}), """
        self.execute_begin_once(cmd)

    def refresh(self, sch: Optional[str] = None) -> dict[str, Any]:
        con = self.eng.connect()
        ses = sessionmaker()(bind=self.eng)
        meta = MetaData()
        meta.reflect(bind=self.eng, schema=sch)
        insp = inspect__(subject=self.eng)
        schema = insp.get_schema_names()
        sch_tab = {k: v for k, v in zip(schema, [insp.get_table_names(schema=x) for x in schema])}
        sch_vws = {k: v for k, v in zip(schema, [insp.get_view_names(schema=x) for x in schema])}
        return {'con': con, 'ses': ses, 'meta': meta, 'insp': insp, 'schema': schema, 'sch_tab': sch_tab, 'sch_vws': sch_vws}

    def get_columns(self, table: str, sch: Optional[str] = None) -> list[str]:
        meta = MetaData()
        meta.reflect(bind=self.eng, schema=sch)
        return list(meta.tables[self._get_table_identifier(self.eng, table, sch)].exported_columns.keys())

    def read_table(self, table: Optional[str] = None, sch: Optional[str] = None, size: int = 5) -> pl.DataFrame:
        insp = inspect__(self.eng)
        schema = insp.get_schema_names()
        sch_tab = {k: v for k, v in zip(schema, [insp.get_table_names(schema=x) for x in schema])}
        if sch is None:
            # First try to find schemas that have tables (excluding system schemas)
            schemas_with_tables = []
            for schema_name in schema:
                if schema_name not in ["information_schema", "pg_catalog", "system"]:
                    if schema_name in sch_tab and len(sch_tab[schema_name]) > 0:
                        schemas_with_tables.append(schema_name)

            if len(schemas_with_tables) == 0:
                raise ValueError(f"No schemas with tables found. Available schemas: {schema}")

            # Prefer non-"main" schemas if available, otherwise use main
            if len(schemas_with_tables) > 1 and "main" in schemas_with_tables:
                sch = [s for s in schemas_with_tables if s != "main"][0]
            else:
                sch = schemas_with_tables[0]
            print(f"Auto-selected schema: `{sch}` from available schemas: {schemas_with_tables}")

        if table is None:
            if sch not in sch_tab:
                raise ValueError(f"Schema `{sch}` not found. Available schemas: {list(sch_tab.keys())}")
            tables = sch_tab[sch]
            assert len(tables) > 0, f"No tables found in schema `{sch}`"
            import random
            table = random.choice(tables)
            print(f"Reading table `{table}` from schema `{sch}`")
        with self.eng.connect() as conn:
            try:
                res = conn.execute(text(f'''SELECT * FROM {self._get_table_identifier(self.eng, table, sch)} '''))
                return pl.DataFrame(res.fetchmany(size))
            except Exception:
                print(f"Error executing query for table `{table}` in schema `{sch}`")
                print(f"Available schemas and tables: {sch_tab}")
                raise

    def describe_db(self, sch: Optional[str] = None) -> pl.DataFrame:
        meta = MetaData()
        meta.reflect(bind=self.eng, schema=sch)
        ses = sessionmaker()(bind=self.eng)
        res_all = []
        from rich.progress import Progress
        with Progress() as progress:
            task = progress.add_task("Inspecting tables", total=len(meta.sorted_tables))
            for tbl in meta.sorted_tables:
                table = tbl.name
                if sch is not None:
                    table = f"{sch}.{table}"
                count = ses.query(tbl).count()
                res = dict(table=table, count=count, size_mb=count * len(tbl.exported_columns) * 10 / 1e6,
                           columns=len(tbl.exported_columns), schema=sch)
                res_all.append(res)
                progress.update(task, advance=1)
        return pl.DataFrame(res_all)

    def describe_table(self, table: str, sch: Optional[str] = None, dtype: bool = True) -> None:
        print(table.center(100, "="))
        meta = MetaData()
        meta.reflect(bind=self.eng, schema=sch)
        tbl = meta.tables[self._get_table_identifier(self.eng, table, sch)]
        ses = sessionmaker()(bind=self.eng)
        count = ses.query(tbl).count()
        res = dict(name=table, count=count, size_mb=count * len(tbl.exported_columns) * 10 / 1e6)
        from machineconfig.utils.accessories import pprint
        pprint(res, title="TABLE DETAILS")
        dat = self.read_table(table=table, sch=sch, size=2)
        df = dat
        print("SAMPLE:\n", df)
        insp = inspect__(self.eng)
        if dtype: print("\nDETAILED COLUMNS:\n", pl.DataFrame(insp.get_columns(self._get_table_identifier(self.eng, table, sch))))
        print("\n" * 3)

    @staticmethod
    def make_sql_engine(path: OPLike = None, echo: bool = False, share_across_threads: bool = False, pool_size: int = 5, **kwargs: Any) -> Engine:
        if path is None:
            url = 'sqlite:///:memory:'
        elif isinstance(path, str) and path.startswith(('sqlite://', 'postgresql://', 'mysql://', 'duckdb://')):
            url = path
        else:
            path_str = str(P(path))
            if path_str.endswith('.duckdb'):
                url = f'duckdb:///{path_str}'
            else:
                url = f'sqlite:///{path_str}'
        connect_args = {}
        if share_across_threads and 'sqlite' in url:
            connect_args['check_same_thread'] = False
        return create_engine(url, echo=echo, pool_size=pool_size, connect_args=connect_args, **kwargs)

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
