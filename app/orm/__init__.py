from os import getenv
from contextlib import contextmanager
from functools import lru_cache
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, Session
from airflow.providers.postgres.hooks.postgres import PostgresHook
from app.tasks import AppContext, get_app_context

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

    def set_client(self, client: str):
        if client:
            db_schema = f"{client}, public, _rrule"
            self.execute(text(f"SET search_path TO {db_schema}"))

@lru_cache
@contextmanager
def get_db_session(connection_id, schema: str|None = None):
    engine = (
        PostgresHook(postgres_conn_id=connection_id)
            .get_sqlalchemy_engine()
    )

    session = ContextSession(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    session.set_schema(schema=schema)

    yield session

    session.close()

@lru_cache
@contextmanager
def get_session(schema: str|None = None, context: AppContext|None = None):
    engine = (
        PostgresHook(postgres_conn_id=getenv('APP__DATABASE__CONN_ID'))
            .get_sqlalchemy_engine()
    )

    session = ContextSession(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    if not context:
        context = get_app_context()

    session.set_schema(schema=schema, context=context)

    yield session

    session.close()
