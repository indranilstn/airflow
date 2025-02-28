import re
from pydantic import BaseModel, Field, EmailStr, field_validator

from sqlalchemy import MetaData, Table, Column, Integer, String
# from sqlalchemy.dialects.postgresql import JSONB

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_contacts_model(metadata: MetaData|None = None):
    tablename = "contacts"

    if sql_model_found:
        class Contact(SQLModel, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            name: str|None = Field(default=None)
            email: EmailStr|None = Field(default=None)
            phone: str|None = Field(default=None)

        return Contact

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String),
            Column("email", String),
            Column("phone", String),
        )

class ProspectData(BaseModel):
    name: str = ""
    email: EmailStr = Field(default="")
    phone: str = ""

    @field_validator("phone")
    def validate_phone_number(cls, v):
        filtered_v = re.sub(r"[\D]+", "", v)

        if len(filtered_v) == 10:
            return filtered_v

        else:
            raise ValueError("Invalid phone number")

