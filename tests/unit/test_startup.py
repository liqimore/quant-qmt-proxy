from __future__ import annotations

from app.config import MarketDataSyncConfig, Settings, XTQuantConfig, XTQuantMode
from app.startup import bootstrap_application, reset_startup_state_for_tests, start_market_data_sync


def test_start_market_data_sync_is_idempotent():
    reset_startup_state_for_tests()
    settings = Settings(
        xtquant=XTQuantConfig(mode=XTQuantMode.MOCK),
        market_data_sync=MarketDataSyncConfig(enabled=True),
    )
    assert start_market_data_sync(settings) is None
    assert start_market_data_sync(settings) is None
    reset_startup_state_for_tests()


def test_ensure_database_ready_is_idempotent(tmp_path):
    reset_startup_state_for_tests()
    settings = Settings(
        database={"url": f"sqlite:///{tmp_path / 'boot.db'}"},
        xtquant=XTQuantConfig(mode=XTQuantMode.MOCK),
    )
    from app.startup import ensure_database_ready

    ensure_database_ready(settings)
    ensure_database_ready(settings)
    reset_startup_state_for_tests()
