from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    from datetime import datetime
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

if sql_model_found:
    class TemporalModel(SQLModel):
        created_at: datetime|None = Field(
            default_factory=lambda: datetime.now(ZoneInfo("UTC")),
            sa_type=DateTime(timezone=True),
            sa_column_kwargs={'server_default': func.timezone("UTC", func.now())}
        )
        update_details: dict = Field(
            default=None,
            sa_type=JSONB,
        )

else:
    class TemporalModel:
        created_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(ZoneInfo("UTC")),
            server_default=func.timezone("UTC", func.now())
        )
        update_details = Column(JSONB, default=None)
