from pathlib import Path
from typing import Callable, Optional, Union, Any, NoReturn, TypeVar, Protocol, List, Generic
import logging
import time
from datetime import datetime, timezone, timedelta
from machineconfig.utils.path_reduced import PathExtended as PathExtended


class LoggerTemplate(Protocol):
    handlers: List[logging.Handler]

    def debug(self, msg: str) -> None:
        pass  # 10

    def info(self, msg: str) -> None:
        pass  # 20

    def warning(self, msg: str) -> None:
        pass  # 30

    def error(self, msg: str) -> None:
        pass  # 40

    def critical(self, msg: str) -> None:
        pass  # 50

    def fatal(self, msg: str) -> None:
        pass  # 50


class Scheduler:
    def __init__(
        self,
        routine: Callable[["Scheduler"], Any],
        wait_ms: int,
        logger: LoggerTemplate,
        sess_stats: Optional[Callable[["Scheduler"], dict[str, Any]]] = None,
        exception_handler: Optional[Callable[[Union[Exception, KeyboardInterrupt], str, "Scheduler"], Any]] = None,
        max_cycles: int = 1_000_000_000,
        records: Optional[list[list[Any]]] = None,
    ):
        self.routine = routine  # main routine to be repeated every `wait` time period
        self.logger = logger
        self.exception_handler = exception_handler if exception_handler is not None else self.default_exception_handler
        self.records: list[list[Any]] = records if records is not None else []
        self.wait_ms = wait_ms  # wait period between routine cycles.
        self.cycle: int = 0
        self.max_cycles: int = max_cycles
        self.sess_start_utc_ms: int
        self.sess_stats = sess_stats or (lambda _sched: {})

    def __repr__(self):
        return f"Scheduler with {self.cycle} cycles ran so far. Last cycle was at {self.sess_start_utc_ms}."

    def run(self, max_cycles: Optional[int] = None, until_ms: Optional[int] = None):
        if max_cycles is not None:
            self.max_cycles = max_cycles
        if until_ms is None:
            until_ms = 1_000_000_000_000_000
        self.sess_start_utc_ms = time.time_ns() // 1_000_000
        while (time.time_ns() // 1_000_000) < until_ms and self.cycle < self.max_cycles:
            # 1- Time before Ops, and Opening Message
            time1_ms = time.time_ns() // 1_000_000
            duration = timedelta(milliseconds=time1_ms - self.sess_start_utc_ms)
            self.logger.info(f"Starting Cycle {str(self.cycle).zfill(5)}. Total Run Time = {str(duration).split('.', maxsplit=1)[0]}. UTC🕜 {datetime.now(tz=timezone.utc).strftime('%d %H:%M:%S')}")
            try:
                self.routine(self)
            except Exception as ex:
                self.exception_handler(ex, "routine", self)  # 2- Perform logic
            time2_ms = time.time_ns() // 1_000_000
            time_left_ms = int(self.wait_ms - (time2_ms - time1_ms))  # 4- Conclude Message
            self.cycle += 1
            self.logger.info(f"Finishing Cycle {str(self.cycle - 1).zfill(5)} in {str((time2_ms - time1_ms) * 0.001).split('.', maxsplit=1)[0]}s. Sleeping for {self.wait_ms * 0.001:0.1f}s ({time_left_ms * 0.001:0.1f}s left)\n" + "-" * 100)
            try:
                time.sleep(time_left_ms * 0.001 if time_left_ms > 0 else 0.0)  # # 5- Sleep. consider replacing by Asyncio.sleep
            except KeyboardInterrupt as ex:
                self.exception_handler(ex, "sleep", self)
                return  # that's probably the only kind of exception that can rise during sleep.
        self.record_session_end(reason=f"Reached maximum number of cycles ({self.max_cycles})" if self.cycle >= self.max_cycles else f"Reached due stop time ({until_ms})")

    def get_records_df(self) -> List[dict[str, Any]]:
        columns = ["start", "finish", "duration", "cycles", "termination reason"] + list(self.sess_stats(self).keys())
        return [dict(zip(columns, row)) for row in self.records]

    def record_session_end(self, reason: str):
        end_time_ms = time.time_ns() // 1_000_000
        duration_ms = end_time_ms - self.sess_start_utc_ms
        sess_stats = self.sess_stats(self)
        self.records.append(
            [
                self.sess_start_utc_ms,
                end_time_ms,
                duration_ms,
                self.cycle,
                reason,
                #  self.logger.file_path
            ]
            + list(sess_stats.values())
        )
        records_df = self.get_records_df()
        total_cycles = sum(row["cycles"] for row in records_df)
        summ = {
            "start time": f"{str(self.sess_start_utc_ms)}",
            "finish time": f"{str(end_time_ms)}.",
            "duration": f"{str(duration_ms)} | wait time {self.wait_ms / 1_000: 0.1f}s",
            "cycles ran": f"{self.cycle} | Lifetime cycles = {total_cycles}",
            "termination reason": reason,
            # "logfile": self.logger.file_path
        }
        summ.update(sess_stats)
        from machineconfig.utils.utils2 import get_repr

        tmp = get_repr(summ)
        self.logger.critical("\n--> Scheduler has finished running a session. \n" + tmp + "\n" + "-" * 100)
        # Format records as table
        if records_df:
            headers = list(records_df[0].keys())
            # Process start, finish, duration to strings without milliseconds
            processed_records = []
            for row in records_df:
                processed = row.copy()
                processed["start"] = str(row["start"]).split(".", maxsplit=1)[0]
                processed["finish"] = str(row["finish"]).split(".", maxsplit=1)[0]
                processed["duration"] = str(row["duration"]).split(".", maxsplit=1)[0]
                processed_records.append(processed)
            # Simple aligned table formatting
            max_lengths = {col: max(len(str(row.get(col, ""))) for row in processed_records) for col in headers}
            table_lines = ["| " + " | ".join(col.ljust(max_lengths[col]) for col in headers) + " |"]
            table_lines.append("|" + "-+-".join("-" * max_lengths[col] for col in headers) + "|")
            for row in processed_records:
                table_lines.append("| " + " | ".join(str(row.get(col, "")).ljust(max_lengths[col]) for col in headers) + " |")
            table_str = "\n".join(table_lines)
        else:
            table_str = "No records available."
        self.logger.critical("\n--> Logger history.\n" + table_str)
        return self

    def default_exception_handler(self, ex: Union[Exception, KeyboardInterrupt], during: str, sched: "Scheduler") -> None:  # user decides on handling and continue, terminate, save checkpoint, etc.  # Use signal library.
        print(sched)
        self.record_session_end(reason=f"during {during}, " + str(ex))
        self.logger.fatal(str(ex))
        raise ex


T = TypeVar("T")
T2 = TypeVar("T2")


class PrintFunc(Protocol):
    def __call__(self, msg: str) -> Union[NoReturn, None]: ...


def to_pickle(obj: Any, path: Path) -> None:
    import pickle

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(obj))


def from_pickle(path: Path) -> Any:
    import pickle

    return pickle.loads(path.read_bytes())


class Cache(Generic[T]):  # This class helps to accelrate access to latest data coming from expensive function. The class has two flavours, memory-based and disk-based variants."""
    # source_func: Callable[[], T]
    def __init__(
        self, source_func: Callable[[], T], expire: timedelta, logger: Optional[PrintFunc] = None, path: Optional[Path] = None, saver: Callable[[T, Path], Any] = to_pickle, reader: Callable[[Path], T] = from_pickle, name: Optional[str] = None
    ) -> None:
        self.cache: T
        self.source_func = source_func  # function which when called returns a fresh object to be frozen.
        self.path: Optional[PathExtended] = PathExtended(path) if path is not None else None  # if path is passed, it will function as disk-based flavour.
        self.time_produced = datetime.now()  # if path is None else
        self.save = saver
        self.reader = reader
        self.logger = logger
        self.expire = expire
        self.name = name if isinstance(name, str) else str(self.source_func)
        self.last_call_is_fresh = False

    @property
    def age(self):
        """Throws AttributeError if called before cache is populated and path doesn't exists"""
        if self.path is None:  # memory-based cache.
            return datetime.now() - self.time_produced
        return datetime.now() - datetime.fromtimestamp(self.path.stat().st_mtime)

    # def __setstate__(self, state: dict[str, Any]) -> None:
    #     self.__dict__.update(state)
    #     self.path = P.home() / self.path if self.path is not None else self.path
    # def __getstate__(self) -> dict[str, Any]:
    #     state = self.__dict__.copy()
    #     state["path"] = self.path.rel2home() if self.path is not None else state["path"]
    #     return state  # With this implementation, instances can be pickled and loaded up in different machine and still works.
    def __call__(self, fresh: bool = False) -> T:
        self.last_call_is_fresh = False
        if fresh or not hasattr(self, "cache"):  # populate cache for the first time
            if not fresh and self.path is not None and self.path.exists():
                age = datetime.now() - datetime.fromtimestamp(self.path.stat().st_mtime)
                msg1 = f"""
📦 ════════════════════ CACHE OPERATION ════════════════════
🔄 {self.name} cache: Reading cached values from `{self.path}`
⏱️  Lag = {age}
════════════════════════════════════════════════════════════
"""
                try:
                    self.cache = self.reader(self.path)
                except Exception as ex:
                    if self.logger:
                        msg2 = f"""
❌ ════════════════════ CACHE ERROR ════════════════════
⚠️  {self.name} cache: Cache file is corrupted
🔍 Error: {ex}
════════════════════════════════════════════════════════
"""
                        self.logger(msg1 + msg2)
                    self.cache = self.source_func()
                    self.last_call_is_fresh = True
                    self.time_produced = datetime.now()
                    # if self.path is not None:
                    #     self.save(self.cache, self.path)
                    return self.cache
                return self(fresh=False)  # may be the cache is old ==> check that by passing it through the logic again.
            else:
                if self.logger:
                    # Previous cache never existed or there was an explicit fresh order.
                    why = "There was an explicit fresh order." if fresh else "Previous cache never existed or is corrupted."
                    self.logger(f"""
🆕 ════════════════════ NEW CACHE ════════════════════
🔄 {self.name} cache: Populating fresh cache from source func
ℹ️  Reason: {why}
════════════════════════════════════════════════════════
""")
                self.cache = self.source_func()  # fresh data.
                self.last_call_is_fresh = True
                self.time_produced = datetime.now()
                if self.path is not None:
                    self.save(self.cache, self.path)
        else:  # cache exists
            try:
                age = self.age
            except AttributeError:  # path doesn't exist (may be deleted) ==> need to repopulate cache form source_func.
                return self(fresh=True)
            if age > self.expire:
                if self.logger:
                    self.logger(f"""
🔄 ════════════════════ CACHE UPDATE ════════════════════
⚠️  {self.name} cache: Updating cache from source func
⏱️  Age = {age} > {self.expire}
════════════════════════════════════════════════════════""")
                self.cache = self.source_func()
                self.last_call_is_fresh = True
                self.time_produced = datetime.now()
                if self.path is not None:
                    self.save(self.cache, self.path)
            else:
                if self.logger:
                    self.logger(f"""
✅ ════════════════════ USING CACHE ════════════════════
📦 {self.name} cache: Using cached values
⏱️  Lag = {age}
════════════════════════════════════════════════════════""")
        return self.cache

    @staticmethod
    def as_decorator(
        expire: timedelta, logger: Optional[PrintFunc] = None, path: Optional[Path] = None, saver: Callable[[T2, Path], Any] = to_pickle, reader: Callable[[Path], T2] = from_pickle, name: Optional[str] = None
    ):  # -> Callable[..., 'Cache[T2]']:
        def decorator(source_func: Callable[[], T2]) -> Cache["T2"]:
            res = Cache(source_func=source_func, expire=expire, logger=logger, path=path, name=name, reader=reader, saver=saver)
            return res

        return decorator

    def from_cloud(self, cloud: str, rel2home: bool = True, root: Optional[str] = None):
        assert self.path is not None
        exists = self.path.exists()
        exists_but_old = exists and ((datetime.now() - datetime.fromtimestamp(self.path.stat().st_mtime)) > self.expire)
        if not exists or exists_but_old:
            returned_path = self.path.from_cloud(cloud=cloud, rel2home=rel2home, root=root)
            if returned_path is None and not exists:
                raise FileNotFoundError(f"❌ Failed to get @ {self.path}. Build the cache first with signed API.")
            elif returned_path is None and exists and self.logger is not None:
                self.logger(f"""
⚠️ ════════════════════ CLOUD FETCH WARNING ════════════════════
🔄 Failed to get fresh data from cloud
📦 Using old cache @ {self.path}
════════════════════════════════════════════════════════════════""")
        else:
            pass  # maybe we don't need to fetch it from cloud, if its too hot
        return self.reader(self.path)
