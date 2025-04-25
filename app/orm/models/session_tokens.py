from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from nanoid import generate as generate_nanoid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal import TemporalModel
from .app_tokens import tablename as token_tablename
from .clients import tablename as clients_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "session_tokens"
_app_key = f"{token_tablename}.id"
_client_key = f"{clients_tablename}.id"

if sql_model_found:
    class SessionToken(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        client_id: int = Field(foreign_key=_client_key)
        app_id: int = Field(foreign_key=_app_key)
        token: str = Field(default_factory=lambda: generate_nanoid(size=14), unique=True)
        valid_till: datetime = Field(
            sa_type=DateTime(timezone=True),
            default_factory=lambda: datetime.now(ZoneInfo("UTC")) + timedelta(hours=1)
        )

        __table_args__ = {
            'schema': "public",
        }

else:
    class SessionToken(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        client_id = Column(Integer, ForeignKey(_client_key))
        app_id = Column(Integer, ForeignKey(_app_key), nullable=False)
        token = Column(String, nullable=False, default=lambda: generate_nanoid(size=14), unique=True)
        valid_till = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC")) + timedelta(hours=1))

        __table_args__ = {
            'schema': "public",
        }
