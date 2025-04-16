from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .. import SQLBase
from .base_temporal import TemporalModel
from .clients import tablename as clients_tablename
from .app_tokens import tablename as app_tablename
from .scopes import tablename as scope_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "app_scopes"
_app_key = f"{app_tablename}.id"
_scope_key = f"{scope_tablename}.id"
_client_key = f"{clients_tablename}.id"

if sql_model_found:
    class AppScope(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        client_id: int = Field(foreign_key=_client_key)
        app_id: int = Field(foreign_key=_app_key)
        scope_id: str = Field(foreign_key=_scope_key)
        default: bool = False

else:
    class AppScope(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        client_id = Column(Integer, ForeignKey(_client_key))
        app_id = Column(String, ForeignKey(_app_key))
        scope_id = Column(String, ForeignKey(_scope_key))
        default = Column(Boolean, default=False)
