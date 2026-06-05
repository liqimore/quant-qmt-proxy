from __future__ import annotations

from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import Engine


def create_db_engine(database_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


def init_db(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
