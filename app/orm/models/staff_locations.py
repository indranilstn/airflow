from enum import Enum
from sqlalchemy import Column, Integer, Enum as SqlEnum, ForeignKey
# from sqlalchemy.ext.associationproxy import association_proxy
# from sqlalchemy.dialects.postgresql import JSONB
from core.utility import enum_values_callable
from .. import SQLBase
from .staff import tablename as staff_table
from .locations import tablename as locations_table

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "staff_locations"
_staff_key = f"{staff_table}.id"
_location_key = f"{locations_table}.id"

class StaffAllotmentType(Enum):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    TEMPORARY = "Temporary"

if sql_model_found:
    class StaffLocation(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        staff_id: int|None = Field(default=None, foreign_key=_staff_key, primary_key=True)
        location_id: int = Field(default=None, foreign_key=_location_key, primary_key=True)
        allotment_type: StaffAllotmentType = Field(
            sa_type=SqlEnum(StaffAllotmentType, values_callable=enum_values_callable),
            default=StaffAllotmentType.PRIMARY
        )

else:
    class StaffLocation(SQLBase):
        __tablename__ = tablename

        staff_id = Column(Integer, ForeignKey(_staff_key), primary_key=True),
        location_id = Column(Integer, ForeignKey(_location_key), primary_key=True),
        allotment_type = Column(
            SqlEnum(StaffAllotmentType, values_callable=enum_values_callable),
            default=StaffAllotmentType.PRIMARY
        )
