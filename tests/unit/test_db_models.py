from __future__ import annotations

from sqlmodel import SQLModel

from app.db import Instrument, SymbolDownload, SyncRun


def test_sqlmodel_metadata_registers_tables():
    table_names = set(SQLModel.metadata.tables)
    assert {"instruments", "sync_runs", "symbol_downloads"}.issubset(table_names)


def test_model_primary_keys():
    assert Instrument.__tablename__ == "instruments"
    assert SyncRun.__tablename__ == "sync_runs"
    assert SymbolDownload.__tablename__ == "symbol_downloads"
