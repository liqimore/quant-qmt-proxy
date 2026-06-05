from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class Instrument(SQLModel, table=True):
    __tablename__ = "instruments"

    symbol: str = Field(primary_key=True)
    name: str
    market: str
    source: str = Field(default="akshare")
    enabled: bool = Field(default=True)
    updated_at: datetime


class SyncRun(SQLModel, table=True):
    __tablename__ = "sync_runs"

    run_date: str = Field(primary_key=True)
    status: str
    instruments_done: bool = Field(default=False)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_summary: str | None = None


class SymbolDownload(SQLModel, table=True):
    __tablename__ = "symbol_downloads"

    run_date: str = Field(primary_key=True)
    symbol: str = Field(primary_key=True)
    period: str = Field(primary_key=True)
    status: str
    attempt_count: int = Field(default=0)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
