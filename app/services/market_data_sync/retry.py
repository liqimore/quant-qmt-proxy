from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def run_with_retries(
    operation: Callable[[], T],
    *,
    max_retries: int,
    backoff_seconds: float,
) -> T:
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(backoff_seconds)
    assert last_error is not None
    raise last_error
