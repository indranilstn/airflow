from sqlalchemy import Column, Integer, String
from .. import SQLBase
from .base_temporal import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "scopes"

if sql_model_found:
    class Scope(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        name: str = Field(unique=True)
        description: str|None = None

else:
    class Scope(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False, unique=True)
        description = Column(String, default=None)
