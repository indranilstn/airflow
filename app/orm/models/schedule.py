from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Enum as SqlEnum, ForeignKey, Index
# from sqlalchemy.dialects.postgresql import JSONB
from core.utility import enum_values_callable
from .staff import tablename as staff_tablename
from .locations import tablename as locations_tablename
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "schedule"
_staff_foreign_key = f"{staff_tablename}.id"
_location_foreign_key = f"{locations_tablename}.id"

class ScheduleType(Enum):
    APPOINTMENT = "Appointment"
    OUT_OF_OFFICE = "Out of Office"
    HOLIDAY = "Holiday"
    LOCATION = "Location"

if sql_model_found:
    class Schedule(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        type: ScheduleType = Field(
            sa_type=SqlEnum(ScheduleType, values_callable=enum_values_callable),
            default=ScheduleType.APPOINTMENT
        )
        agent_id: int|None = Field(default=None, foreign_key=_staff_foreign_key)
        location_id: int|None = Field(default=None, foreign_key=_location_foreign_key)
        start: datetime = Field(sa_type=DateTime(True))
        end: datetime = Field(sa_type=DateTime(True))

        __table_args__ = (
            Index("agent_id", "location_id", name="schedule_agent_location_idx"),
            Index(
                "agent_id",
                "start",
                name="schedule_agent_start_uid",
                unique=True,
                postgresql_where=(type == ScheduleType.APPOINTMENT)
            ),
        )

else:
    class Schedule(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        type = Column(SqlEnum(ScheduleType, values_callable=enum_values_callable), default=ScheduleType.APPOINTMENT)
        agent_id = Column(Integer, ForeignKey(_staff_foreign_key), default=None)
        location_id = Column(Integer, ForeignKey(_location_foreign_key), default=None)
        start = Column(DateTime(True))
        end = Column(DateTime(True))

        __table_args__ = (
            Index("agent_id", "location_id", name="schedule_agent_location_idx"),
            Index(
                "agent_id",
                "start",
                name="schedule_agent_start_uid",
                unique=True,
                postgresql_where=(type == ScheduleType.APPOINTMENT)
            ),
        )
