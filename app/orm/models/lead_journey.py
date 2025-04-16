from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal_update import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "lead_journey"
_events_key = "events.id"
_locations_key = "locations.id"
_master_key = "contact_master.id"

if sql_model_found:
    class LeadJourney(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        event_id: int = Field(nullable=False, foreign_key=_events_key, unique=True)
        location_id: int = Field(nullable=False, foreign_key=_locations_key)
        primary_master_id: int = Field(nullable=False, foreign_key=_master_key)
        secondary_master_id: int|None = Field(foreign_key=_master_key)

else:
    class LeadJourney(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        event_id = Column(Integer, ForeignKey(_events_key), nullable=False, unique=True)
        location_id = Column(Integer, ForeignKey(_locations_key), nullable=False)
        primary_master_id = Column(String, ForeignKey(_master_key), nullable=False)
        secondary_master_id = Column(String, ForeignKey(_master_key))
