from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter

from utils.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def timed(label: str):
    start = perf_counter()
    try:
        yield
    finally:
        logger.info("%s took %.3fs", label, perf_counter() - start)
