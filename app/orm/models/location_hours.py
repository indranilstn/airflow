from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
# from .base_temporal import TemporalModel
from .locations import tablename as locations_tablename

try:
    from sqlmodel import Field, SQLModel # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "location_hours"
_locations_key = f"{locations_tablename}.id"

class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

if sql_model_found:
    class LocationHour(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        location_id: int = Field(foreign_key=_locations_key, primary_key=True)
        working_hours: dict = Field(
            sa_type=JSONB,
            default_factory=lambda: {
                Weekday.MONDAY: ["09:00:00", "18:00:00"],
                Weekday.TUESDAY: ["09:00:00", "18:00:00"],
                Weekday.WEDNESDAY: ["09:00:00", "18:00:00"],
                Weekday.THURSDAY: ["09:00:00", "18:00:00"],
                Weekday.FRIDAY: ["09:00:00", "18:00:00"],
                Weekday.SATURDAY: ["09:00:00", "14:00:00"],
                Weekday.SUNDAY: ["00:00:00", "00:00:00"],
            }
        )

else:
    class LocationHour(SQLBase):
        __tablename__ = tablename

        location_id = Column(Integer, ForeignKey(_locations_key), primary_key=True)
        working_hours = Column(
            JSONB,
            default=lambda: {
                Weekday.MONDAY: ["09:00:00", "18:00:00"],
                Weekday.TUESDAY: ["09:00:00", "18:00:00"],
                Weekday.WEDNESDAY: ["09:00:00", "18:00:00"],
                Weekday.THURSDAY: ["09:00:00", "18:00:00"],
                Weekday.FRIDAY: ["09:00:00", "18:00:00"],
                Weekday.SATURDAY: ["09:00:00", "14:00:00"],
                Weekday.SUNDAY: ["00:00:00", "00:00:00"],
            }
        )
