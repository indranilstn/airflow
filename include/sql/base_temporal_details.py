from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def base_temporal_model():
    if sql_model_found:
        class BaseTemporal(SQLModel):
            created_at: DateTime|None = Field(
                default=None,
                sa_column_kwargs={'server_default': func.now()}
            ),
            update_details: dict = Field(
                default=None,
                sa_type=JSONB,
            )

        return BaseTemporal

    else:
        return (
            Column("created_at", DateTime(), server_default=func.now()),
            Column("update_details", JSONB, default=None),
        )
