from enum import Enum
from sqlalchemy import MetaData, Table, Column, Integer, String, Enum as SqlEnum, UniqueConstraint
# from sqlalchemy.dialects.postgresql import JSONB

class ContactAssocType(Enum):
    EMAIL = "Email"
    PHONE = "Phone"

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_contact_master_model(metadata: MetaData|None = None):
    tablename = "contact_master"

    if sql_model_found:
        class ContactMaster(SQLModel, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            value: str
            type: ContactAssocType = Field(default=ContactAssocType.EMAIL)

            __table_args__ = (
                UniqueConstraint("value", "type", name="uix_value_type_master"),
            )

        return ContactMaster

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("value", String),
            Column("type", SqlEnum(ContactAssocType, values_callable=lambda x: [e.value for e in x]), default=ContactAssocType.EMAIL),
            UniqueConstraint("value", "type", name="uix_value_type_master"),
        )
