from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SqlEnum, UniqueConstraint
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase

class ContactAssocType(Enum):
    EMAIL = "Email"
    PHONE = "Phone"

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "contact_master"

if sql_model_found:
    class ContactMaster(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        value: str
        type: ContactAssocType = Field(default=ContactAssocType.EMAIL)

        __table_args__ = (
            UniqueConstraint("value", "type", name="contact_master_value_type_uidx"),
        )

else:
    class ContactMaster(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        value = Column("value", String)
        type = Column(SqlEnum(ContactAssocType, values_callable=lambda x: [e.value for e in x]), default=ContactAssocType.EMAIL)

        __table_args__ = (
            UniqueConstraint("value", "type", name="contact_master_value_type_uidx"),
        )
