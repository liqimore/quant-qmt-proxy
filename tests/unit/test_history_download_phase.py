from __future__ import annotations

from app.services.market_data_sync.phases import HistoryDownloadPhase
from tests.unit.market_data_sync_helpers import make_repository


class FakeGateway:
    def __init__(self):
        self.calls: list[tuple[str, str, bool]] = []

    def download_history_data(self, symbol: str, period: str, *, incrementally: bool = True) -> None:
        self.calls.append((symbol, period, incrementally))


def test_downloads_1d_before_1m_per_symbol(tmp_path):
    repo = make_repository(tmp_path)
    gateway = FakeGateway()
    phase = HistoryDownloadPhase(
        repo,
        gateway,
        periods=["1d", "1m"],
        concurrency=1,
        max_retries=0,
        retry_backoff_seconds=0,
        fail_fast=False,
    )
    phase.run("2026-06-03", ["000001.SZ"])
    assert gateway.calls == [
        ("000001.SZ", "1d", True),
        ("000001.SZ", "1m", True),
    ]


def test_skips_completed_symbol_period(tmp_path):
    repo = make_repository(tmp_path)
    repo.mark_symbol_period_completed("2026-06-03", "000001.SZ", "1d", attempt_count=1)
    gateway = FakeGateway()
    phase = HistoryDownloadPhase(
        repo,
        gateway,
        periods=["1d", "1m"],
        concurrency=1,
        max_retries=0,
        retry_backoff_seconds=0,
        fail_fast=False,
    )
    phase.run("2026-06-03", ["000001.SZ"])
    assert gateway.calls == [("000001.SZ", "1m", True)]
