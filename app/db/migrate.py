from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

from app.db.engine import create_db_engine, init_db
from app.utils.logger import logger


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _alembic_config(database_url: str) -> Config:
    root = _project_root()
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def upgrade_database(database_url: str) -> Engine:
    """Apply Alembic migrations on startup (no separate CLI required)."""
    engine = create_db_engine(database_url)
    try:
        command.upgrade(_alembic_config(database_url), "head")
        logger.info(f"database migrations applied: {database_url}")
    except Exception as exc:
        logger.warning(f"alembic upgrade failed, falling back to create_all: {exc}")
        init_db(engine)
    return engine


def resolve_database_url(database_url: str | None) -> str:
    return database_url or "sqlite:///./app_sync.db"
