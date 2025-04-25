from nanoid import generate as generate_nanoid
from sqlalchemy import Column, Integer, String
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal_update import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "clients"

default_rate_limit = 1000

if sql_model_found:
    class Client(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        marker: str = Field(default=lambda: generate_nanoid(size=14), unique=True)
        name: str = Field(unique=True)
        address: str|None = Field(sa_type=String(1000), default=None)
        rate_limit: int = default_rate_limit

        __table_args__ = {
            'schema': "public",
        }

else:
    class Client(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        marker = Column(String, nullable=False, default=lambda: generate_nanoid(size=14), unique=True)
        name = Column(String, nullable=False, index=True)
        address = Column(String(1000), default=None)
        rate_limit = Column(Integer, default=default_rate_limit)

        __table_args__ = {
            'schema': "public",
        }
