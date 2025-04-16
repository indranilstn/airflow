from datetime import date as DateClass, time
from sqlalchemy import Column, Integer, SmallInteger, Date, Time, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB
from .staff import tablename as staff_tablename
from .locations import tablename as locations_tablename
from .schedule import tablename as schedule_tablename
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "busy_slots"
_staff_foreign_key = f"{staff_tablename}.id"
_location_foreign_key = f"{locations_tablename}.id"
_schedule_foreign_key = f"{schedule_tablename}.id"

if sql_model_found:
    class BusySlot(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        schedule_id: int = Field(foreign_key=_schedule_foreign_key)
        agent_id: int|None = Field(default=None, foreign_key=_staff_foreign_key)
        location_id: int|None = Field(default=None, foreign_key=_location_foreign_key)
        date: DateClass = Field(sa_type=Date())
        start: time = Field(sa_type=Time())
        end: time = Field(sa_type=Time())
        count: int = Field(sa_type=SmallInteger, default=0)

else:
    class BusySlot(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        schedule_id = Column(Integer, ForeignKey(_schedule_foreign_key))
        agent_id = Column(Integer, ForeignKey(_staff_foreign_key), default=None)
        location_id = Column(Integer, ForeignKey(_location_foreign_key), default=None)
        date = Column(Date())
        start = Column(Time())
        end = Column(Time())
        count = Column(SmallInteger, default=0)
