from __future__ import annotations

from app.config import MarketDataSyncConfig, Settings, XTQuantConfig, XTQuantMode
from app.services.market_data_sync.scheduler import MarketDataSyncScheduler


def test_scheduler_not_started_when_disabled():
    settings = Settings(
        xtquant=XTQuantConfig(mode=XTQuantMode.MOCK),
        market_data_sync=MarketDataSyncConfig(enabled=False),
    )
    scheduler = MarketDataSyncScheduler(settings, service_factory=lambda: None)
    scheduler.start()
    assert scheduler.running is False


def test_mock_mode_forces_disabled_even_if_enabled_flag():
    settings = Settings(
        xtquant=XTQuantConfig(mode=XTQuantMode.MOCK),
        market_data_sync=MarketDataSyncConfig(enabled=True),
    )
    assert settings.market_data_sync_effective_enabled() is False
