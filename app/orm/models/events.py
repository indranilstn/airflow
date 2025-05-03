from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.core.utility import enum_values_callable
from .. import SQLBase
from .base_temporal import TemporalModel
from .contacts import tablename as contacts_tablename
from .locations import tablename as locations_tablename

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

class EventType(Enum):
    EMAIL = "Email"
    BOOKING = "Booking"

tablename = "events"
_contacts_key = f"{contacts_tablename}.id"
_locations_key = f"{locations_tablename}.id"

if sql_model_found:
    class Event(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        type: EventType = Field(sa_type=SqlEnum(EventType, values_callable=enum_values_callable), default=EventType.EMAIL)
        contact_id: int|None = Field(default=None, foreign_key=_contacts_key)
        source: str|None = Field(default=None)
        unit_type: str|None = Field(default=None)
        location_id: int|None = Field(default=None, foreign_key=_locations_key)
        data: dict|None = Field(default=None, sa_type=JSONB)

else:
    class Event(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        type = Column(SqlEnum(EventType, values_callable=enum_values_callable), default=EventType.EMAIL)
        contact_id = Column(Integer, ForeignKey(_contacts_key), default=None)
        source = Column(String, default=None)
        unit_type = Column(String, default=None)
        location_id = Column(Integer, ForeignKey(_locations_key), default=None)
        data = Column(JSONB, default=None)
