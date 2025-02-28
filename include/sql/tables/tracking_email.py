from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB

from ..base_temporal_details import base_temporal_model

try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_tracking_email(metadata: MetaData|None = None):
    base_model = base_temporal_model()

    if sql_model_found:
        class TrackerEmail(base_model, table=True):
            id: int | None = Field(default=None, primary_key=True)
            headers: dict = Field(sa_type=JSONB)
            body: dict = Field(sa_type=JSONB)
            msg_id: str = Field(unique=True)

        return TrackerEmail

    elif metadata:
        return Table(
            "tracker_email",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("headers", JSONB),
            Column("body", JSONB),
            Column("msg_id", JSONB, unique=True),
            *base_model
        )
