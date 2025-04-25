from nanoid import generate as generate_nanoid
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal import TemporalModel
from .cities import tablename as cities_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "locations"
_self_reference_key = "locations.id"
_city_key = f"{cities_tablename}.id"

if sql_model_found:
    class Location(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        master_id: int|None = Field(sa_type=String(24), default=None, foreign_key=_self_reference_key)
        marker: str = Field(sa_type=String(24), default=lambda: generate_nanoid(size=14), unique=True)
        name: str = Field(sa_type=String(254))
        address: str|None = Field(sa_type=String(1000), default=None)
        city_id: int = Field(foreign_key=_city_key)
        postal_code: str|None = Field(sa_type=String(10), default=None)

        __table_args__ = (
            UniqueConstraint("name", "city_id", name="locations_name_city_id_uidx"),
        )

else:
    class Location(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        master_id = Column(Integer, ForeignKey(_self_reference_key), default=None)
        marker = Column(String(24), nullable=False, default=lambda: generate_nanoid(size=14), unique=True)
        name = Column(String(254), nullable=False)
        address = Column(String(1000), default=None)
        city_id = Column(Integer, ForeignKey(_city_key))
        postal_code = Column(String(10), default=None)

        __table_args__ = (
            UniqueConstraint("name", "city_id", name="locations_name_city_id_uidx"),
        )
