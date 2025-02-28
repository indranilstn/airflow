from enum import Enum
from pydantic import Field

from sqlalchemy import MetaData, Table, Column, Integer, String, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from include.sql.base_temporal import base_temporal_model
try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

class EventType(Enum):
    EMAIL = "Email"

def _values_callable(obj):
    return [e.value for e in obj]

def get_events_model(metadata: MetaData|None = None):
    tablename = "events"
    temporal_model = base_temporal_model()

    if sql_model_found:
        class Event(temporal_model, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            type: EventType = Field(sa_type=SqlEnum(EventType, values_callable=_values_callable), default=EventType.EMAIL)
            contact_id: int|None = Field(default=None, foreigh_key="contact.id")
            source: str|None = Field(default=None)
            unit_type: str|None = Field(default=None)
            location_marker: str|None = Field(default=None)
            data: dict|None = Field(default=None, sa_type=JSONB)

        return Event

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("type", SqlEnum(EventType, values_callable=_values_callable), default=EventType.EMAIL),
            Column("contact_id", Integer, ForeignKey("contacts.id"), default=None),
            Column("source", String, default=None),
            Column("unit_type", String, default=None),
            Column("location_marker", String, default=None),
            Column("data", JSONB, default=None),
            *temporal_model
        )
