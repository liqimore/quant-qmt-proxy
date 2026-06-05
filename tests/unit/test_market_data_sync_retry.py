from __future__ import annotations

import pytest

from app.services.market_data_sync.retry import run_with_retries


def test_run_with_retries_succeeds_on_third_attempt():
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("fail")
        return "ok"

    assert run_with_retries(flaky, max_retries=2, backoff_seconds=0) == "ok"
    assert calls["n"] == 3


def test_run_with_retries_raises_after_exhausted():
    def always_fail() -> None:
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        run_with_retries(always_fail, max_retries=2, backoff_seconds=0)
