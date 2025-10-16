


from pathlib import Path
from typing import Any, Optional


class Read:
    @staticmethod
    def read(path: 'Path', **kwargs: Any) -> Any:
        if Path(path).is_dir(): raise IsADirectoryError(f"Path is a directory, not a file: {path}")
        suffix = Path(path).suffix[1:]
        if suffix == "": raise ValueError(f"File type could not be inferred from suffix. Suffix is empty. Path: {path}")
        if suffix in ("sqlite", "sqlite3", "db", "duckdb"):
            from machineconfig.utils.files.dbms import DBMS
            res = DBMS.from_local_db(path=path)
            print(res.describe_db())
            return res
        try: return getattr(Read, suffix)(str(path), **kwargs)
        except AttributeError as err:
            if "type object 'Read' has no attribute" not in str(err): raise AttributeError(err) from err
            if suffix in ('eps', 'jpg', 'jpeg', 'pdf', 'pgf', 'png', 'ps', 'raw', 'rgba', 'svg', 'svgz', 'tif', 'tiff'):
                import matplotlib.pyplot as pyplot
                return pyplot.imread(str(path), **kwargs)  # from: plt.gcf().canvas.get_supported_filetypes().keys():
            if suffix == "parquet":
                import polars as pl
                return pl.read_parquet(path, **kwargs)
            elif suffix == "csv":
                import polars as pl
                return pl.read_csv(path, **kwargs)
            try:
                # guess = install_n_import('magic', 'python-magic').from_file(path)
                guess = "IDKm"
                raise AttributeError(f"Unknown file type. failed to recognize the suffix `{suffix}`. According to libmagic1, the file seems to be: {guess}") from err
            except ImportError as err2:
                print(f"💥 Unknown file type. failed to recognize the suffix `{suffix}` of file {path} ")
                raise ImportError(err) from err2
    @staticmethod
    def json(path: 'Path', r: bool = False, **kwargs: Any) -> Any:  # return could be list or dict etc
        from machineconfig.utils.io import read_json
        return read_json(path, r=r, **kwargs)
    @staticmethod
    def yaml(path: 'Path', r: bool = False) -> Any:  # return could be list or dict etc
        import yaml
        with open(str(path), "r", encoding="utf-8") as file:
            mydict = yaml.load(file, Loader=yaml.FullLoader)
        _ = r
        return mydict
    @staticmethod
    def ini(path: 'Path', encoding: Optional[str] = None):
        if not Path(path).exists() or Path(path).is_dir(): raise FileNotFoundError(f"File not found or is a directory: {path}")
        import configparser
        res = configparser.ConfigParser()
        res.read(filenames=[str(path)], encoding=encoding)
        return res
    @staticmethod
    def toml(path: 'Path'):
        import tomllib
        return tomllib.loads(Path(path).read_text(encoding='utf-8'))
    @staticmethod
    def npy(path: 'Path', **kwargs: Any):
        import numpy as np
        data = np.load(str(path), allow_pickle=True, **kwargs)
        # data = data.item() if data.dtype == np.object else data
        return data
    @staticmethod
    def pickle(path: 'Path', **kwargs: Any):
        import pickle
        try: return pickle.loads(Path(path).read_bytes(), **kwargs)
        except BaseException as ex:
            print(f"💥 Failed to load pickle file `{path}` with error:\n{ex}")
            raise ex
    @staticmethod
    def pkl(path: 'Path', **kwargs: Any): return Read.pickle(path, **kwargs)
    # @staticmethod
    # def dill(path: 'Path', **kwargs: Any) -> Any:
    #     """handles imports automatically provided that saved object was from an imported class (not in defined in __main__)"""
    #     import dill
    #     obj = dill.loads(str=Path(path).read_bytes(), **kwargs)
    #     return obj
    @staticmethod
    def py(path: 'Path', init_globals: Optional[dict[str, Any]] = None, run_name: Optional[str] = None):
        import runpy
        return runpy.run_path(str(path), init_globals=init_globals, run_name=run_name)
    @staticmethod
    def txt(path: 'Path', encoding: str = 'utf-8') -> str: return Path(path).read_text(encoding=encoding)
    @staticmethod
    def parquet(path: 'Path', **kwargs: Any):
        import polars as pl
        return pl.read_parquet(path, **kwargs)



if __name__ == '__main__':
    pass
