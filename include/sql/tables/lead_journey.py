from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
# from sqlalchemy.dialects.postgresql import JSONB

from include.sql.base_temporal import base_temporal_model
try:
    from sqlmodel import Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_journey_model(metadata: MetaData|None = None):
    tablename = "lead_journey"
    temporal_model = base_temporal_model()

    if sql_model_found:
        class LeadJourney(temporal_model, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            event_id: int = Field(nullable=False, foreign_key="events.id", unique=True)
            location_id: int = Field(nullable=False, foreign_key="locations.id")
            primary_master_id: int = Field(nullable=False, foreign_key="contact_master.id")
            secondary_master_id: int|None = Field(foreign_key="contact_master.id")

        return LeadJourney

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("event_id", Integer, ForeignKey("events.id"), nullable=False, unique=True),
            Column("location_id", Integer, ForeignKey("locations.id"), nullable=False),
            Column("primary_master_id", String, ForeignKey("contact_master.id"), nullable=False),
            Column("secondary_master_id", String, ForeignKey("contact_master.id")),
            *temporal_model
        )
