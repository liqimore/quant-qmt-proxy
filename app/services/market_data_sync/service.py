from __future__ import annotations

from datetime import date

from app.config import Settings
from app.services.instrument_repository import InstrumentRepository
from app.services.market_data_sync.phases import HistoryDownloadPhase, InstrumentSyncPhase
from app.utils.logger import logger


class MarketDataSyncService:
    def __init__(
        self,
        settings: Settings,
        repository: InstrumentRepository,
        instrument_phase: InstrumentSyncPhase,
        history_phase: HistoryDownloadPhase,
    ):
        self.settings = settings
        self.repository = repository
        self.instrument_phase = instrument_phase
        self.history_phase = history_phase

    def run_daily_if_needed(self) -> None:
        if not self.settings.market_data_sync_effective_enabled():
            logger.debug("market data sync disabled for current mode")
            return

        run_date = date.today().isoformat()
        if self.repository.should_skip_daily_run(run_date):
            logger.info(f"market data sync skipped: run_date={run_date} already completed")
            return

        sync_cfg = self.settings.market_data_sync
        self.repository.mark_run_running(run_date)
        logger.info(f"market data sync started: run_date={run_date}")

        try:
            if not self.repository.instruments_synced_today(run_date):
                self.instrument_phase.run(run_date)
        except Exception as exc:
            self.repository.mark_run_failed(run_date, f"instrument sync failed: {exc}")
            logger.error(f"market data sync failed in instrument phase: {exc}")
            return

        symbols = sync_cfg.symbols_override or self.repository.list_enabled_symbols()
        try:
            self.history_phase.run(run_date, symbols)
        except Exception as exc:
            self.repository.mark_run_failed(run_date, f"history download failed: {exc}")
            logger.error(f"market data sync failed in history phase: {exc}")
            return

        if self.repository.has_failed_downloads(run_date):
            self.repository.mark_run_failed(run_date, "one or more symbol downloads failed")
            logger.warning(f"market data sync finished with failures: run_date={run_date}")
            return

        self.repository.mark_run_completed(run_date)
        logger.info(f"market data sync completed: run_date={run_date}")
