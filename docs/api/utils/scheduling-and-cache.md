# Scheduling and Cache

`machineconfig.utils.scheduler` currently contains three distinct utilities:

| API | Role |
| --- | --- |
| `Scheduler` | Repeatedly run a routine with lifecycle logging and session recording |
| `CacheMemory[T]` | Keep an in-memory cached value around a source function |
| `Cache[T]` | Add disk-backed cache-file reuse on top of similar refresh logic |

---

## `Scheduler`

A `Scheduler` is constructed from:

- `routine`, which receives the current scheduler instance
- `wait_ms`
- `logger`
- optional `sess_stats`
- optional `exception_handler`
- optional `max_cycles`
- optional `records`

Current runtime behavior:

- `run()` loops until it reaches `max_cycles` or `until_ms`
- each cycle logs a start message, calls `routine(self)`, increments `cycle`, logs a finish message, then sleeps
- `record_session_end()` appends a row into `records`, builds a summary, and logs the accumulated session history
- `get_records_df()` returns the recorded sessions as a list of dictionaries
- the default exception handler records the session end, logs the failure, and re-raises the exception

So this is more than a bare `while True` loop: it keeps a session ledger and provides a consistent shutdown summary.

---

## `CacheMemory`

`CacheMemory` wraps a zero-argument `source_func` and stores the result in memory.

Constructor inputs:

- `source_func`
- `expire`
- `logger`
- optional `name`

Current refresh semantics are important:

- first access populates the cache
- `fresh=True` always repopulates immediately
- otherwise it refreshes only when the cached age is greater than `expire`

`tolerance_seconds` is accepted for API parity, but in the current `CacheMemory` implementation it does not control refresh behavior once the wrapper reaches the main cache path.

`CacheMemory.as_decorator(...)` returns a `CacheMemory` wrapper object around the decorated function.

---

## `Cache`

`Cache` keeps the same source function idea, but adds a disk file and pluggable serialization.

Constructor inputs:

- `source_func`
- `expire`
- `logger`
- `path`
- optional `saver`
- optional `reader`
- optional `name`

Current behavior differs from `CacheMemory` in two ways:

1. On first access, if the cache file already exists, `Cache` prefers reading it from disk before calling `source_func`.
2. `fresh=True` is tolerance-aware instead of unconditional.

More precisely:

- if no in-memory cache exists and the cache file exists, the file is reused when it is young enough
- if the file is too old, or `fresh=True` and the file age exceeds `tolerance_seconds`, the wrapper regenerates from `source_func`
- if the file exists but the reader raises, the wrapper regenerates, rewrites the file, and continues
- once the in-memory cache is populated, later calls refresh when age exceeds `expire`, or when `fresh=True` and age exceeds `tolerance_seconds`

By default, `Cache` uses `to_pickle()` and `from_pickle()`, but you can swap in other saver / reader pairs.

`Cache.as_decorator(...)` also returns a cache wrapper object rather than the raw function result.

---

## Example usage

```python
from datetime import timedelta
from pathlib import Path

from machineconfig.logger import get_logger
from machineconfig.utils.scheduler import Cache, CacheMemory, Scheduler

logger = get_logger("demo")


def fetch_snapshot() -> dict[str, float]:
    return {"btc": 100_000.0}


memory_cache = CacheMemory(
    source_func=fetch_snapshot,
    expire=timedelta(seconds=30),
    logger=logger,
)

disk_cache = Cache(
    source_func=fetch_snapshot,
    expire=timedelta(minutes=5),
    logger=logger,
    path=Path("tmp/snapshot.pkl"),
)


def routine(scheduler: Scheduler) -> None:
    logger.info("cycle=%s memory=%s", scheduler.cycle, memory_cache(fresh=False, tolerance_seconds=0))
    logger.info("cycle=%s disk=%s", scheduler.cycle, disk_cache(fresh=False, tolerance_seconds=0))


Scheduler(
    routine=routine,
    wait_ms=5_000,
    logger=logger,
    max_cycles=3,
).run()
```

---

## API reference

::: machineconfig.utils.scheduler
    options:
      show_root_heading: true
      show_source: false
      members_order: source
