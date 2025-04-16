from sqlalchemy import Column, Integer, ForeignKey
# from sqlalchemy.ext.associationproxy import association_proxy
# from sqlalchemy.dialects.postgresql import JSONB
from .. import SQLBase
from .contact_master import tablename as master_table
from .contacts import tablename as contact_table

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

tablename = "contact_assoc"

if sql_model_found:
    class ContactAssoc(SQLModel, table=True, metadata=SQLBase.metadata):
        __tablename__ = tablename

        master_id: int|None = Field(default=None, foreign_key=f"{master_table}.id", primary_key=True)
        contact_id: int = Field(default=None, foreign_key=f"{contact_table}.id", primary_key=True)

else:
    class ContactAssoc(SQLBase):
        __tablename__ = tablename

        master_id = Column(Integer, ForeignKey(f"{master_table}.id"), primary_key=True),
        contact_id = Column(Integer, ForeignKey(f"{contact_table}.id"), primary_key=True),
