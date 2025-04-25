from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .base_temporal_update import TemporalModel

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "tracker_email"

if sql_model_found:
    class TrackerEmail(TemporalModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int | None = Field(default=None, primary_key=True)
        headers: dict = Field(sa_type=JSONB)
        body: dict = Field(sa_type=JSONB)
        msg_id: str = Field(unique=True)
        is_processed: bool = False

        __table_args__ = {
            'schema': "public",
        }

else:
    class TrackerEmail(SQLBase, TemporalModel):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        headers = Column(JSONB)
        body = Column(JSONB)
        msg_id = Column(JSONB, unique=True)
        is_processed = Column(Boolean, default=False)

        __table_args__ = {
            'schema': "public",
        }
