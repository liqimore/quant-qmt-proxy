from app.config import MarketDataSyncConfig, Settings


def test_market_data_sync_defaults():
    cfg = MarketDataSyncConfig()
    assert cfg.enabled is False
    assert cfg.periods == ["1d", "1m"]
    assert cfg.concurrency == 3
    assert cfg.max_retries == 2
    assert cfg.cron_time == "18:00"


def test_settings_embeds_market_data_sync():
    settings = Settings(market_data_sync=MarketDataSyncConfig(enabled=True))
    assert settings.market_data_sync.enabled is True
