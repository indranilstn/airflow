from sqlalchemy import MetaData, Table, Column, Integer, UniqueConstraint
# from sqlalchemy.dialects.postgresql import JSONB

try:
    from sqlmodel import SQLModel, Field # type: ignore import error
    sql_model_found = True
except ModuleNotFoundError:
    sql_model_found = False

def get_contact_assoc_model(metadata: MetaData|None = None):
    tablename = "contact_assoc"

    if sql_model_found:
        class ContactAssoc(SQLModel, table=True):
            __tablename__ = tablename

            id: int|None = Field(default=None, primary_key=True)
            master_id: int
            contact_id: int

            __table_args__ = (
                UniqueConstraint("master_id", "contact_id", name="uix_master_contact_assoc"),
            )

        return ContactAssoc

    elif metadata:
        return Table(
            tablename,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("master_id", Integer, nullable=False),
            Column("contact_id", Integer, nullable=False),
            UniqueConstraint("master_id", "contact_id", name="uix_master_contact_assoc"),
        )
