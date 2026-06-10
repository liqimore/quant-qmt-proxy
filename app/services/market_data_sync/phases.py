from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.instrument_repository import InstrumentRepository
from app.services.market_data_sync.akshare_client import FetchRowsFn, default_fetch_rows
from app.services.market_data_sync.retry import run_with_retries
from app.services.xtdata_gateway import XtDataGateway
from app.utils.logger import logger


class InstrumentSyncPhase:
    def __init__(
        self,
        repository: InstrumentRepository,
        *,
        fetch_rows: FetchRowsFn | None = None,
        max_retries: int = 2,
        retry_backoff_seconds: float = 1.0,
    ):
        self.repository = repository
        self._fetch_rows = fetch_rows or default_fetch_rows
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds

    def run(self, run_date: str) -> None:
        def sync_once() -> None:
            rows = self._fetch_rows()
            if not rows:
                raise RuntimeError("akshare returned zero instruments")
            self.repository.upsert_instruments(rows)

        run_with_retries(
            sync_once,
            max_retries=self._max_retries,
            backoff_seconds=self._retry_backoff_seconds,
        )
        self.repository.set_instruments_done(run_date)
        logger.info(f"instrument sync completed for run_date={run_date}")


class HistoryDownloadPhase:
    def __init__(
        self,
        repository: InstrumentRepository,
        gateway: XtDataGateway,
        *,
        periods: list[str],
        concurrency: int,
        max_retries: int,
        retry_backoff_seconds: float,
        fail_fast: bool,
    ):
        self.repository = repository
        self.gateway = gateway
        self.periods = periods
        self.concurrency = concurrency
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self.fail_fast = fail_fast

    def run(self, run_date: str, symbols: list[str]) -> None:
        if not symbols:
            logger.warning(f"no symbols to download for run_date={run_date}")
            return

        def download_symbol(symbol: str) -> None:
            for period in self.periods:
                if self.repository.is_symbol_period_completed(run_date, symbol, period):
                    continue
                attempt_counter = {"count": 0}

                def download_once() -> None:
                    attempt_counter["count"] += 1
                    self.gateway.download_history_data(symbol, period, incrementally=True)

                try:
                    run_with_retries(
                        download_once,
                        max_retries=self._max_retries,
                        backoff_seconds=self._retry_backoff_seconds,
                    )
                    self.repository.mark_symbol_period_completed(
                        run_date,
                        symbol,
                        period,
                        attempt_count=attempt_counter["count"],
                    )
                except Exception as exc:
                    self.repository.mark_symbol_period_failed(
                        run_date,
                        symbol,
                        period,
                        attempt_count=attempt_counter["count"] or self._max_retries + 1,
                        error_message=str(exc),
                    )
                    logger.error(
                        f"download failed: run_date={run_date} symbol={symbol} period={period} error={exc}"
                    )
                    if self.fail_fast:
                        raise

        stop_flag = {"abort": False}

        def download_symbol_with_flag(symbol: str) -> None:
            if stop_flag["abort"]:
                return
            download_symbol(symbol)

        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = {executor.submit(download_symbol_with_flag, symbol): symbol for symbol in symbols}
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                except Exception:
                    if self.fail_fast:
                        stop_flag["abort"] = True
                    raise
