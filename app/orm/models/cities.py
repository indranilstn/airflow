from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from .. import SQLBase
from .country_states import tablename as states_tablename

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "cities"
_state_key = f"{states_tablename}.id"

if sql_model_found:
    class City(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        name: str = Field(sa_type=String(254))
        state_id: int = Field(foreign_key=_state_key)
        timezone: str = Field(sa_type=String(100))

        __table_args__ = (
            UniqueConstraint("name", "state_id", name="cities_name_state_id_uidx"),
            { 'schema': "public", },
        )

else:
    class City(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(254), nullable=False)
        state_id = Column(Integer, ForeignKey(_state_key), nullable=False)
        timezone = Column(String(100), nullable=False)

        __table_args__ = (
            UniqueConstraint("name", "state_id", name="cities_name_state_id_uidx"),
            { 'schema': "public", },
        )
