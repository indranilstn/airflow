from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, Session
from airflow.providers.postgres.hooks.postgres import PostgresHook
from app.tasks import AppContext

SQLBase = declarative_base()

class ContextSession(Session):
    def set_schema(self, schema: str|None = None, context: AppContext|None = None):
        db_schema = "public"

        if schema:
            db_schema = schema

        elif context:
            client = context.get("client", None)
            if client:
                db_schema = f"{client}, public, _rrule"

        self.execute(text(f"SET search_path TO {db_schema}"))

@contextmanager
def get_pg_session(connection_id, schema: str|None = None, context: AppContext|None = None):
    engine = (
        PostgresHook(postgres_conn_id=connection_id)
            .get_sqlalchemy_engine()
    )

    session = ContextSession(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    session.set_schema(schema=schema, context=context)

    yield session

    session.close()
