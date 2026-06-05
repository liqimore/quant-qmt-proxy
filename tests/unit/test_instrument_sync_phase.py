from __future__ import annotations

from app.services.market_data_sync.phases import InstrumentSyncPhase
from tests.unit.market_data_sync_helpers import make_repository


def test_instrument_sync_upserts_rows(tmp_path):
    repo = make_repository(tmp_path)
    repo.mark_run_running("2026-06-03")

    def fetch_rows():
        return [
            {
                "symbol": "600000.SH",
                "name": "PFYH",
                "market": "SH",
                "source": "akshare",
                "enabled": True,
            }
        ]

    phase = InstrumentSyncPhase(repo, fetch_rows=fetch_rows, max_retries=0, retry_backoff_seconds=0)
    phase.run("2026-06-03")
    assert repo.list_enabled_symbols() == ["600000.SH"]
    assert repo.instruments_synced_today("2026-06-03") is True
