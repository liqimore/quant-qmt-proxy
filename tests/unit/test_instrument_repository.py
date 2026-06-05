from __future__ import annotations

from tests.unit.market_data_sync_helpers import make_repository


def test_upsert_and_list_enabled(tmp_path):
    repo = make_repository(tmp_path)
    repo.upsert_instruments(
        [{"symbol": "600000.SH", "name": "PFYH", "market": "SH", "enabled": True}]
    )
    assert repo.list_enabled_symbols() == ["600000.SH"]


def test_sync_run_lifecycle(tmp_path):
    repo = make_repository(tmp_path)
    today = "2026-06-03"
    assert repo.get_run_status(today) is None
    repo.mark_run_running(today)
    assert repo.get_run_status(today) == "running"
    repo.mark_run_completed(today)
    assert repo.get_run_status(today) == "completed"
    assert repo.should_skip_daily_run(today) is True
