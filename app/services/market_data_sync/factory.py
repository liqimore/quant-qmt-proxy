from __future__ import annotations

from app.config import Settings
from app.db.engine import create_db_engine
from app.db.migrate import resolve_database_url
from app.services.instrument_repository import InstrumentRepository
from app.services.market_data_sync.phases import HistoryDownloadPhase, InstrumentSyncPhase
from app.services.market_data_sync.service import MarketDataSyncService
from app.services.xtdata_gateway import XtDataGateway


def build_market_data_sync_service(
    settings: Settings,
    gateway: XtDataGateway | None = None,
) -> MarketDataSyncService:
    engine = create_db_engine(resolve_database_url(settings.database.url))
    repository = InstrumentRepository(engine)

    sync_cfg = settings.market_data_sync
    xt_gateway = gateway or XtDataGateway(settings)
    instrument_phase = InstrumentSyncPhase(
        repository,
        max_retries=sync_cfg.max_retries,
        retry_backoff_seconds=sync_cfg.retry_backoff_seconds,
    )
    history_phase = HistoryDownloadPhase(
        repository,
        xt_gateway,
        periods=list(sync_cfg.periods),
        concurrency=sync_cfg.concurrency,
        max_retries=sync_cfg.max_retries,
        retry_backoff_seconds=sync_cfg.retry_backoff_seconds,
        fail_fast=sync_cfg.fail_fast,
    )
    return MarketDataSyncService(settings, repository, instrument_phase, history_phase)
