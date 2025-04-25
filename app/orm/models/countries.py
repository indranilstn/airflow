from sqlalchemy import Column, Integer, String
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "countries"

if sql_model_found:
    class Country(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        name: str = Field(sa_type=String(254), unique=True)
        iso2: str = Field(sa_type=String(2), unique=True)
        division_name: str|None = Field(sa_type=String(100), default=None)

        __table_args__ = {
            'schema': "public",
        }

else:
    class Country(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(254), nullable=False, unique=True)
        iso2 = Column(String(2), nullable=False, unique=True)
        division_name = Column(String(100), default=None)

        __table_args__ = {
            'schema': "public",
        }
