import re
from pydantic import BaseModel, Field, EmailStr, field_validator
from sqlalchemy import Column, Integer, String
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "contacts"

if sql_model_found:
    class Contact(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        id: int|None = Field(default=None, primary_key=True)
        name: str|None = Field(default=None)
        email: EmailStr|None = Field(default=None)
        phone: str|None = Field(default=None)

else:
    class Contact(SQLBase):
        __tablename__ = tablename

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String)
        email = Column(String)
        phone = Column(String)

class ProspectData(BaseModel):
    name: str|None = None
    email: EmailStr|None = None
    phone: str|None = None

    @field_validator("phone")
    def validate_phone_number(cls, v):
        filtered_v = re.sub(r"[\D]+", "", v)

        if len(filtered_v) == 10:
            return filtered_v

        else:
            raise ValueError("Invalid phone number")
