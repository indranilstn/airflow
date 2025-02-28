from nanoid import generate as generate_nano
from pydantic import Field

from sqlalchemy import MetaData, Table, Column, Integer, String
# from sqlalchemy.dialects.postgresql import JSONB

from include.sql.base_temporal import base_temporal_model
try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_locations_model(metadata: MetaData|None = None):
    tablename = "locations"
    temporal_model = base_temporal_model()

    if sql_model_found:
        class Event(temporal_model, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            master_id: int|None = Field(default=None, index=True)
            marker: str = Field(default=lambda: generate_nano(12), index=True)
            name: str = Field(index=True)
            address: str|None = Field(default=None)

        return Event

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("master_id", Integer, default=None, index=True),
            Column("marker", String, nullable=False, default=lambda: nanoid(12), index=True),
            Column("name", String, nullable=False, index=True),
            Column("address", String, default=None),
            *temporal_model
        )
