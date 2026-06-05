from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.db.models import Instrument, SymbolDownload, SyncRun


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InstrumentRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    def init_schema(self) -> None:
        from app.db.engine import init_db

        init_db(self._engine)

    def upsert_instruments(self, rows: list[dict[str, Any]]) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            for row in rows:
                session.merge(
                    Instrument(
                        symbol=row["symbol"],
                        name=row["name"],
                        market=row["market"],
                        source=row.get("source", "akshare"),
                        enabled=bool(row.get("enabled", True)),
                        updated_at=now,
                    )
                )
            session.commit()

    def list_enabled_symbols(self) -> list[str]:
        with Session(self._engine) as session:
            statement = (
                select(Instrument.symbol).where(Instrument.enabled.is_(True)).order_by(Instrument.symbol)
            )
            return list(session.exec(statement).all())

    def get_run_status(self, run_date: str) -> str | None:
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            return run.status if run else None

    def should_skip_daily_run(self, run_date: str) -> bool:
        return self.get_run_status(run_date) == "completed"

    def mark_run_running(self, run_date: str) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            if run is None:
                run = SyncRun(run_date=run_date, status="running", started_at=now)
            else:
                run.status = "running"
                run.started_at = now
                run.finished_at = None
                run.error_summary = None
            session.add(run)
            session.commit()

    def set_instruments_done(self, run_date: str) -> None:
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            if run is None:
                run = SyncRun(run_date=run_date, status="running", instruments_done=True)
            else:
                run.instruments_done = True
            session.add(run)
            session.commit()

    def instruments_synced_today(self, run_date: str) -> bool:
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            return bool(run and run.instruments_done)

    def mark_run_completed(self, run_date: str) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            if run is None:
                run = SyncRun(run_date=run_date, status="completed", finished_at=now)
            else:
                run.status = "completed"
                run.finished_at = now
                run.error_summary = None
            session.add(run)
            session.commit()

    def mark_run_failed(self, run_date: str, error_summary: str) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            run = session.get(SyncRun, run_date)
            if run is None:
                run = SyncRun(
                    run_date=run_date,
                    status="failed",
                    finished_at=now,
                    error_summary=error_summary,
                )
            else:
                run.status = "failed"
                run.finished_at = now
                run.error_summary = error_summary
            session.add(run)
            session.commit()

    def is_symbol_period_completed(self, run_date: str, symbol: str, period: str) -> bool:
        with Session(self._engine) as session:
            record = session.get(SymbolDownload, (run_date, symbol, period))
            return bool(record and record.status == "completed")

    def mark_symbol_period_completed(
        self,
        run_date: str,
        symbol: str,
        period: str,
        attempt_count: int,
    ) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            record = session.get(SymbolDownload, (run_date, symbol, period))
            if record is None:
                record = SymbolDownload(
                    run_date=run_date,
                    symbol=symbol,
                    period=period,
                    status="completed",
                    attempt_count=attempt_count,
                    finished_at=now,
                )
            else:
                record.status = "completed"
                record.attempt_count = attempt_count
                record.finished_at = now
                record.error_message = None
            session.add(record)
            session.commit()

    def mark_symbol_period_failed(
        self,
        run_date: str,
        symbol: str,
        period: str,
        attempt_count: int,
        error_message: str,
    ) -> None:
        now = _utc_now()
        with Session(self._engine) as session:
            record = session.get(SymbolDownload, (run_date, symbol, period))
            if record is None:
                record = SymbolDownload(
                    run_date=run_date,
                    symbol=symbol,
                    period=period,
                    status="failed",
                    attempt_count=attempt_count,
                    finished_at=now,
                    error_message=error_message,
                )
            else:
                record.status = "failed"
                record.attempt_count = attempt_count
                record.finished_at = now
                record.error_message = error_message
            session.add(record)
            session.commit()

    def has_failed_downloads(self, run_date: str) -> bool:
        with Session(self._engine) as session:
            statement = (
                select(SymbolDownload.run_date)
                .where(SymbolDownload.run_date == run_date)
                .where(SymbolDownload.status == "failed")
                .limit(1)
            )
            return session.exec(statement).first() is not None
