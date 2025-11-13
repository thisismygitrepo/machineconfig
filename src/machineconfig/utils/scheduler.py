
from pathlib import Path
from typing import Callable, Optional, Union, Any, Protocol, List, TypeVar
# import logging
import time
from datetime import datetime, timezone, timedelta
from machineconfig.utils.io import from_pickle


class LoggerTemplate(Protocol):
    def trace(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 5
    def success(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 25
    def debug(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 10
    def info(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 20
    def warning(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 30
    def error(self,  __message: str, *args: Any, **kwargs: Any) -> None:
        pass  # 40
    def critical(self,  __message: str, *args: Any, **kwargs: Any) -> None:
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
        from machineconfig.utils.accessories import get_repr

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
        self.logger.critical(str(ex))
        raise ex


# T = TypeVar("T")
T2 = TypeVar("T2")
def to_pickle(obj: Any, path: Path) -> None:
    import pickle
    path.write_bytes(pickle.dumps(obj))


class CacheMemory[T]():
    def __init__(
        self, source_func: Callable[[], T], expire: timedelta, logger: LoggerTemplate, name: Optional[str] = None
    ) -> None:
        self.cache: T
        self.source_func = source_func
        self.time_produced = datetime.now()
        self.logger = logger
        self.expire = expire
        self.name = name if isinstance(name, str) else self.source_func.__name__
    def __call__(self, fresh: bool, tolerance_seconds: float | int) -> T:
        if fresh or not hasattr(self, "cache"):
            why = "There was an explicit fresh order." if fresh else "Previous cache never existed."
            t0 = time.time()
            self.logger.warning(f"""🆕  NEW CACHE 🔄 {self.name} CACHE ℹ️ Reason: {why}""")
            self.cache = self.source_func()
            self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
            self.time_produced = datetime.now()
        else:
            age = datetime.now() - self.time_produced
            if (age > self.expire) or (fresh and (age.total_seconds() > tolerance_seconds)):
                self.logger.warning(f"""🔄 CACHE UPDATE ⚠️  {self.name} cache: Updating cache from source func. """ + f""" ⏱️  Age = {age} > {self.expire}""" if not fresh else f""" ⏱️  Age = {age}. Fresh flag raised.""")
                t0 = time.time()
                self.cache = self.source_func()
                self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
                self.time_produced = datetime.now()
            else:
                self.logger.warning(f"""✅ USING CACHE 📦 {self.name} cache: Using cached values ⏱️  Lag = {age} < {self.expire} < {tolerance_seconds} seconds.""")
        return self.cache

    @staticmethod
    def as_decorator(expire: timedelta, logger: LoggerTemplate, name: Optional[str] = None):
        def decorator(source_func: Callable[[], T2]) -> CacheMemory["T2"]:
            res = CacheMemory(source_func=source_func, expire=expire, logger=logger, name=name)
            return res
        return decorator


class Cache[T]():  # This class helps to accelrate access to latest data coming from expensive function. The class has two flavours, memory-based and disk-based variants."""
    def __init__(
        self, source_func: Callable[[], T], expire: timedelta, logger: LoggerTemplate, path: Path, saver: Callable[[T, Path], Any] = to_pickle, reader: Callable[[Path], T] = from_pickle, name: Optional[str] = None
    ) -> None:
        self.cache: T
        self.source_func = source_func  # function which when called returns a fresh object to be frozen.
        self.path: Path = path
        _ = self.path.parent.mkdir(parents=True, exist_ok=True)
        self.time_produced = datetime.now()  # if path is None else
        self.save = saver
        self.reader = reader
        self.logger = logger
        self.expire = expire
        self.name = name if isinstance(name, str) else self.source_func.__name__
    def __call__(self, fresh: bool, tolerance_seconds: float | int) -> T:
        if not hasattr(self, "cache"):  # populate cache for the first time: we have two options, populate from disk or from source func.
            if self.path.exists():  # prefer to read from disk over source func as a default source of cache.
                age = datetime.now() - datetime.fromtimestamp(self.path.stat().st_mtime)
                if (age > self.expire) or (fresh and (age.total_seconds() > tolerance_seconds)):  # cache is old or if fresh flag is raised
                    self.logger.warning(f"""🔄 CACHE STALE 📦 {self.name} cache: Populating fresh cache from source func. """ + f"""⏱️  Age = {age} > Expiry {self.expire} """ if not fresh else """⚠️  Fresh flag raised.""")
                    t0 = time.time()
                    self.cache = self.source_func()  # fresh data.
                    self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
                    self.time_produced = datetime.now()
                    self.save(self.cache, self.path)
                    return self.cache
                msg1 = f"""📦 CACHE OPERATION 🔄 {self.name} cache: Reading cached values from `{self.path}` ⏱️  Lag = {age}"""
                try:
                    self.cache = self.reader(self.path)
                except Exception as ex:
                    msg2 = f"""❌ CACHE ERROR ⚠️  {self.name} cache: Cache file is corrupted 🔍 Error: {ex}"""
                    self.logger.warning(msg1 + msg2)
                    t0 = time.time()
                    self.cache = self.source_func()
                    self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
                    self.time_produced = datetime.now()
                    self.save(self.cache, self.path)
                    return self.cache
            else:  # disk cache does not exist, populate from source func.
                self.logger.warning(f"""🆕  NEW CACHE 🔄 {self.name} cache: Populating fresh cache from source func ℹ️  Reason: Previous cache never existed.""")
                t0 = time.time()
                self.cache = self.source_func()  # fresh data.
                self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
                self.time_produced = datetime.now()
                self.save(self.cache, self.path)
        else:  # memory cache exists
            age = datetime.now() - self.time_produced
            if (age > self.expire) or (fresh and (age.total_seconds() > tolerance_seconds)):  # cache is old or if fresh flag is raised
                self.logger.warning(f"""🔄 CACHE UPDATE ⚠️  {self.name} cache: Updating cache from source func. ⏱️  Age = {age} > {self.expire}""")
                t0 = time.time()
                self.cache = self.source_func()
                self.logger.warning(f"⏱️  Cache population took {time.time() - t0:.2f} seconds.")
                self.time_produced = datetime.now()
                self.save(self.cache, self.path)
            else:
                self.logger.warning(f"""✅ USING CACHE 📦 {self.name} cache: Using cached values ⏱️  Lag = {age} < {self.expire} < {tolerance_seconds} seconds.""")
        return self.cache

    @staticmethod
    def as_decorator(
        expire: timedelta, logger: LoggerTemplate, path: Path, saver: Callable[[T2, Path], Any] = to_pickle, reader: Callable[[Path], T2] = from_pickle, name: Optional[str] = None
    ):  # -> Callable[..., 'Cache[T2]']:
        def decorator(source_func: Callable[[], T2]) -> Cache["T2"]:
            res = Cache(source_func=source_func, expire=expire, logger=logger, path=path, name=name, reader=reader, saver=saver)
            return res
        return decorator
