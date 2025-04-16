from nanoid import generate as generate_nanoid
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "locations"
_self_reference_key = "locations.id"

if sql_model_found:
    class Location(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        master_id: int|None = Field(default=None, foreign_key=_self_reference_key)
        marker: str = Field(default=lambda: generate_nanoid(size=14), unique=True)
        name: str = Field(unique=True)
        address: str|None = Field(default=None)

else:
    class Location(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        master_id = Column(Integer, ForeignKey(_self_reference_key), default=None)
        marker = Column(String, nullable=False, default=lambda: generate_nanoid(size=12), unique=True)
        name = Column(String, nullable=False, unique=True)
        address = Column(String, default=None)
