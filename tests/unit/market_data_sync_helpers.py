from __future__ import annotations

from pathlib import Path

from app.db.engine import create_db_engine
from app.services.instrument_repository import InstrumentRepository


def make_repository(tmp_path: Path, db_name: str = "sync.db") -> InstrumentRepository:
    engine = create_db_engine(f"sqlite:///{tmp_path / db_name}")
    repository = InstrumentRepository(engine)
    repository.init_schema()
    return repository
