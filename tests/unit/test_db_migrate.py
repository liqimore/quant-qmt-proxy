from __future__ import annotations

from sqlalchemy import inspect

from app.db.migrate import upgrade_database


def test_upgrade_database_creates_tables(tmp_path):
    db_path = tmp_path / "migrate.db"
    engine = upgrade_database(f"sqlite:///{db_path}")
    table_names = set(inspect(engine).get_table_names())
    assert {"instruments", "sync_runs", "symbol_downloads"}.issubset(table_names)
