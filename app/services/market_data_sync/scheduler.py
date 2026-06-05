from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import Settings
from app.services.market_data_sync.factory import build_market_data_sync_service
from app.services.market_data_sync.service import MarketDataSyncService
from app.utils.logger import logger


def parse_cron_time(cron_time: str) -> tuple[int, int]:
    parts = cron_time.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"invalid cron_time, expected HH:MM: {cron_time!r}")
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"invalid cron_time: {cron_time!r}")
    return hour, minute


class MarketDataSyncScheduler:
    def __init__(
        self,
        settings: Settings,
        service_factory: Callable[[], MarketDataSyncService] | None = None,
    ):
        self.settings = settings
        self._service_factory = service_factory or (
            lambda: build_market_data_sync_service(settings)
        )
        self._scheduler: BackgroundScheduler | None = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="market-data-sync")

    @property
    def running(self) -> bool:
        return bool(self._scheduler and self._scheduler.running)

    def _build_service(self) -> MarketDataSyncService:
        return self._service_factory()

    def _run_sync_job(self) -> None:
        try:
            self._build_service().run_daily_if_needed()
        except Exception as exc:
            logger.exception(f"market data sync job failed: {exc}")

    def start(self) -> None:
        if not self.settings.market_data_sync_effective_enabled():
            logger.info("market data sync scheduler not started (disabled or mock mode)")
            return

        sync_cfg = self.settings.market_data_sync
        hour, minute = parse_cron_time(sync_cfg.cron_time)
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(
            self._run_sync_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="market_data_sync_daily",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info(f"market data sync scheduler started: daily at {sync_cfg.cron_time}")

        if sync_cfg.on_startup:
            self._executor.submit(self._run_sync_job)

    def shutdown(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        self._executor.shutdown(wait=False, cancel_futures=True)
        logger.info("market data sync scheduler stopped")
