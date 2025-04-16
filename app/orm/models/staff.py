from sqlalchemy import Column, Integer, String
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "staff"

if sql_model_found:
    class Staff(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        name: str|None = Field(default=None)
        email: str|None = Field(default=None)
        phone: str|None = Field(default=None)

else:
    class Staff(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String)
        email = Column(String)
        phone = Column(String)
