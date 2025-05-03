from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
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
        updated_at: datetime|None = Field(
            default=None,
            sa_column_kwargs={'onupdate': func.timezone("UTC", func.now())} # onupdate may not work - bug #4652
        )

else:
    class TemporalModel:
        created_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(ZoneInfo("UTC")),
            server_default=func.timezone("UTC", func.now())
        )
        updated_at = Column(
            DateTime(timezone=True),
            nullable=True,
            default=None,
            onupdate=func.timezone("UTC", func.now())
        )
