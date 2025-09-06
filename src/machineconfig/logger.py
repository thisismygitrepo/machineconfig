from __future__ import annotations

import logging
import os
import sys
from typing import Optional


def _configure_root_logger() -> logging.Logger:
    """Create and configure the root logger for the machineconfig package.

    The logger writes to stdout, honors MC_LOG_LEVEL env var, and avoids
    duplicate handlers on repeated imports.
    """
    root = logging.getLogger("machineconfig")
    if root.handlers:
        return root

    level_name = os.getenv("MC_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%H:%M:%S"
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    root.addHandler(handler)
    root.propagate = False
    return root


_ROOT_LOGGER = _configure_root_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger of the package root.

    Inputs:
    - name: Optional dotted logger name; when None, returns the package root.

    Returns:
    - logging.Logger configured under the 'machineconfig' hierarchy.
    """
    if name is None:
        return _ROOT_LOGGER
    return _ROOT_LOGGER.getChild(name)


# Convenience alias for simple imports: `from machineconfig.logger import logger`
logger: logging.Logger = get_logger()
