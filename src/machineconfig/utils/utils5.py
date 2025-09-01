
from typing import Callable, Optional, Union, Any
from logging import Logger as Log
from machineconfig.utils.utils2 import randstr, get_repr
import time
from datetime import datetime, timezone


class Scheduler:
    def __init__(self, routine: Callable[['Scheduler'], Any],
                 wait_ms: int,
                 exception_handler: Optional[Callable[[Union[Exception, KeyboardInterrupt], str, 'Scheduler'], Any]] = None,
                 logger: Optional[Log] = None,
                 sess_stats: Optional[Callable[['Scheduler'], dict[str, Any]]] = None,
                 max_cycles: int = 1_000_000_000,
                 records: Optional[list[list[Any]]] = None):
        self.routine = routine  # main routine to be repeated every `wait` time period
        self.logger = logger if logger is not None else Log(name="SchedLogger_" + randstr(noun=True))
        self.exception_handler = exception_handler if exception_handler is not None else self.default_exception_handler
        self.records: list[list[Any]] = records if records is not None else []
        self.wait_ms = wait_ms  # wait period between routine cycles.
        self.cycle: int = 0
        self.max_cycles: int = max_cycles
        self.sess_start_time_ms: int
        self.sess_stats = sess_stats or (lambda _sched: {})
    def __repr__(self): return f"Scheduler with {self.cycle} cycles ran so far. Last cycle was at {self.sess_start_time_ms}."
    def run(self, max_cycles: Optional[int]=None, until_ms: Optional[int]=None):
        if max_cycles is not None:
            self.max_cycles = max_cycles
        if until_ms is None:
            until_ms = 1_000_000_000_000
        self.sess_start_time_ms = time.time_ns() // 1_000_000
        while (time.time_ns() // 1_000_000) < until_ms and self.cycle < self.max_cycles:
            # 1- Time before Ops, and Opening Message
            time1_ms = time.time_ns() // 1_000_000
            self.logger.info(f"Starting Cycle {str(self.cycle).zfill(5)}. Total Run Time = {str(time1_ms - self.sess_start_time_ms).split('.', maxsplit=1)[0]}. UTC🕜 {datetime.now(tz=timezone.utc).strftime('%d %H:%M:%S')}")
            try:
                self.routine(self)
            except Exception as ex:
                self.exception_handler(ex, "routine", self)  # 2- Perform logic
            time2_ms = time.time_ns() // 1_000_000
            time_left_ms = int(self.wait_ms - (time2_ms - time1_ms))  # 4- Conclude Message
            self.cycle += 1
            self.logger.info(f"Finishing Cycle {str(self.cycle - 1).zfill(5)} in {str((time2_ms - time1_ms)*0.001).split('.', maxsplit=1)[0]}s. Sleeping for {self.wait_ms*0.001:0.1f}s ({time_left_ms*0.001:0.1}s left)\n" + "-" * 100)
            try: time.sleep(time_left_ms*0.001 if time_left_ms > 0 else 0.0)  # # 5- Sleep. consider replacing by Asyncio.sleep
            except KeyboardInterrupt as ex:
                self.exception_handler(ex, "sleep", self)
                return  # that's probably the only kind of exception that can rise during sleep.
        self.record_session_end(reason=f"Reached maximum number of cycles ({self.max_cycles})" if self.cycle >= self.max_cycles else f"Reached due stop time ({until_ms})")
    def get_records_df(self):
        import polars as pl
        columns = ["start", "finish", "duration", "cycles", "termination reason", "logfile"] + list(self.sess_stats(self).keys())
        return pl.DataFrame(self.records, schema=columns)
    def record_session_end(self, reason: str):
        import polars as pl
        end_time_ms = time.time_ns() // 1_000_000
        duration_ms = end_time_ms - self.sess_start_time_ms
        sess_stats = self.sess_stats(self)
        self.records.append([self.sess_start_time_ms, end_time_ms, duration_ms, self.cycle, reason,
                            #  self.logger.file_path
                             ] + list(sess_stats.values()))
        summ = {"start time": f"{str(self.sess_start_time_ms)}",
                "finish time": f"{str(end_time_ms)}.",
                "duration": f"{str(duration_ms)} | wait time {self.wait_ms/1_000: 0.1f}s",
                "cycles ran": f"{self.cycle} | Lifetime cycles = {self.get_records_df().select(pl.col('cycles').sum()).item()}",
                "termination reason": reason,
                # "logfile": self.logger.file_path
                }
        summ.update(sess_stats)
        tmp = get_repr(summ)
        self.logger.critical("\n--> Scheduler has finished running a session. \n" + tmp + "\n" + "-" * 100)
        df = self.get_records_df()
        df = df.with_columns([
            pl.col("start").map_elements(lambda x: str(x).split(".", maxsplit=1)[0], return_dtype=pl.String),
            pl.col("finish").map_elements(lambda x: str(x).split(".", maxsplit=1)[0], return_dtype=pl.String),
            pl.col("duration").map_elements(lambda x: str(x).split(".", maxsplit=1)[0], return_dtype=pl.String)
        ])
        self.logger.critical("\n--> Logger history.\n" + str(df))
        return self
    def default_exception_handler(self, ex: Union[Exception, KeyboardInterrupt], during: str, sched: 'Scheduler') -> None:  # user decides on handling and continue, terminate, save checkpoint, etc.  # Use signal library.
        print(sched)
        self.record_session_end(reason=f"during {during}, " + str(ex))
        self.logger.exception(ex)
        raise ex
