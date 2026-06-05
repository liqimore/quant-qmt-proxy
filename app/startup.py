from __future__ import annotations

from app.config import Settings
from app.db.migrate import resolve_database_url, upgrade_database
from app.services.market_data_sync.scheduler import MarketDataSyncScheduler
from app.utils.logger import logger

_market_data_sync_scheduler: MarketDataSyncScheduler | None = None
_database_ready = False


def ensure_database_ready(settings: Settings) -> None:
    global _database_ready
    if _database_ready:
        return
    database_url = resolve_database_url(settings.database.url)
    upgrade_database(database_url)
    _database_ready = True


def start_market_data_sync(settings: Settings) -> MarketDataSyncScheduler | None:
    global _market_data_sync_scheduler
    if _market_data_sync_scheduler is not None:
        return _market_data_sync_scheduler

    if not settings.market_data_sync_effective_enabled():
        logger.info("market data sync not started (disabled or mock mode)")
        return None

    _market_data_sync_scheduler = MarketDataSyncScheduler(settings)
    _market_data_sync_scheduler.start()
    return _market_data_sync_scheduler


def stop_market_data_sync() -> None:
    global _market_data_sync_scheduler
    if _market_data_sync_scheduler is None:
        return
    _market_data_sync_scheduler.shutdown()
    _market_data_sync_scheduler = None


def bootstrap_application(settings: Settings) -> None:
    """Run DB migrations and optional market-data sync when the process starts."""
    ensure_database_ready(settings)
    start_market_data_sync(settings)


def shutdown_application() -> None:
    stop_market_data_sync()


def reset_startup_state_for_tests() -> None:
    global _database_ready, _market_data_sync_scheduler
    stop_market_data_sync()
    _database_ready = False
    _market_data_sync_scheduler = None
