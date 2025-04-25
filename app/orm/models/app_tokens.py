from nanoid import generate as generate_nanoid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal_update import TemporalModel
from .clients import tablename as clients_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "app_tokens"
_client_key = f"public.{clients_tablename}.id"

if sql_model_found:
    class AppToken(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        client_id: int = Field(foreign_key=_client_key)
        app: str = Field(unique=True)
        token: str = Field(default_factory=lambda: generate_nanoid(size=14), unique=True)
        active: bool = True

        __table_args__ = {
            'schema': "public",
        }

else:
    class AppToken(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        client_id = Column(Integer, ForeignKey(_client_key))
        app = Column(String, nullable=False, unique=True)
        token = Column(String, nullable=False, default=lambda: generate_nanoid(size=14))
        active = Column(Boolean, default=True)

        __table_args__ = {
            'schema': "public",
        }
