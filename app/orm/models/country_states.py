from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from .. import SQLBase
from .countries import tablename as countries_tablename

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "country_states"
_country_key = f"{countries_tablename}.id"

if sql_model_found:
    class Country(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        state: str = Field(sa_type=String(254))
        iso2: str = Field(sa_type=String(2))
        country_id: int = Field(foreign_key=_country_key)

        __table_args__ = (
            UniqueConstraint("state", "country_id", name="country_states_state_country_id_uidx"),
            UniqueConstraint("iso2", "country_id", name="country_states_iso2_country_id_uidx"),
            { 'schema': "public", },
        )

else:
    class Country(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        state = Column(String(254), nullable=False)
        iso2 = Column(String(2), nullable=False)
        country_id = Column(Integer, ForeignKey(_country_key), nullable=False)

        __table_args__ = (
            UniqueConstraint("state", "country_id", name="country_states_state_country_id_uidx"),
            UniqueConstraint("iso2", "country_id", name="country_states_iso2_country_id_uidx"),
            { 'schema': "public", },
        )
