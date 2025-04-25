from sqlalchemy import Column, Integer, String, ForeignKey
from .. import SQLBase
from .base_temporal import TemporalModel
from .clients import tablename as clients_tablename
from .session_tokens import tablename as session_tablename
from .scopes import tablename as scope_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "token_scopes"
_token_key = f"{session_tablename}.id"
_scope_key = f"{scope_tablename}.id"
_client_key = f"{clients_tablename}.id"

if sql_model_found:
    class TokenScope(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        client_id: int = Field(foreign_key=_client_key)
        token_id: int = Field(foreign_key=_token_key)
        scope_id: int = Field(foreign_key=_scope_key)

        __table_args__ = {
            'schema': "public",
        }

else:
    class TokenScope(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        client_id = Column(Integer, ForeignKey(_client_key))
        token_id = Column(String, ForeignKey(_token_key))
        scope_id = Column(Integer, ForeignKey(_scope_key))

        __table_args__ = {
            'schema': "public",
        }
