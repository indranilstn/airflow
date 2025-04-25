from enum import Enum
# from pydantic import BaseModel, Field, EmailStr, field_validator
from sqlalchemy import Column, Integer, Enum as SqlEnum, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB
from core.utility import enum_values_callable
from .events import tablename as events_tablename
from .schedule import tablename as schedule_tablename
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "bookings"
_events_foreign_key = f"{events_tablename}.id"
_shed_foreign_key = f"{schedule_tablename}.id"

class BookingStatus(Enum):
    OPEN = 1
    CLOSED = 2
    RESCHED = 3

if sql_model_found:
    class Booking(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        event_id: int = Field(foreign_key=_events_foreign_key)
        schedule_id: int = Field(foreign_key=_shed_foreign_key)
        status: BookingStatus = Field(
            sa_type=SqlEnum(BookingStatus, values_callable=enum_values_callable),
            default=BookingStatus.OPEN
        )

else:
    class Booking(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        event_id = Column(Integer, ForeignKey(_events_foreign_key))
        schedule_id = Column(Integer, ForeignKey(_shed_foreign_key))
        status = Column(SqlEnum(BookingStatus, values_callable=enum_values_callable), default=BookingStatus.OPEN)
