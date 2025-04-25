from enum import Enum
from sqlalchemy import Column, Integer, Boolean, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from app.core.utility import enum_values_callable
from .. import SQLBase
from .base_temporal_update import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "service_requests"

class ServiceRequestType(Enum):
    SCHEDULE_EMAIL_DELIVERY = "email_delivery"

if sql_model_found:
    class ServiceRequest(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int | None = Field(default=None, primary_key=True)
        type: ServiceRequestType = Field(
            sa_type=SqlEnum(ServiceRequestType, values_callable=enum_values_callable),
            default=ServiceRequestType.SCHEDULE_EMAIL_DELIVERY,
        )
        data: dict = Field(sa_type=JSONB)
        is_processed: bool = False

        __table_args__ = {
            'schema': "public",
        }

else:
    class ServiceRequest(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        type = Column(
            SqlEnum(ServiceRequestType, values_callable=enum_values_callable),
            default=ServiceRequestType.SCHEDULE_EMAIL_DELIVERY,
        )
        data = Column(JSONB)
        is_processed = Column(Boolean, default=False)

        __table_args__ = {
            'schema': "public",
        }
