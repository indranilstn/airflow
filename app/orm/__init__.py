from typing import override
from os import getenv
from contextlib import contextmanager
from functools import lru_cache
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from airflow.providers.postgres.hooks.postgres import PostgresHook
from app.tasks import AppContext, get_app_context

session_config = {
    'sync': True
}

SQLBase = declarative_base()

class ContextSession(Session):
    def __init__(self, bind=None, autoflush=True, future=False, expire_on_commit=True, autocommit=False, twophase=False, binds=None, enable_baked_queries=True, info=None, query_cls=None):
        super().__init__(bind, autoflush, future, expire_on_commit, autocommit, twophase, binds, enable_baked_queries, info, query_cls)
        self.current_path = None

    def set_schema(self, schema: str|None = None, context: AppContext|None = None) -> None:
        db_schema = "public"

        if schema:
            db_schema = schema

        elif context:
            client = context.get("client", None)
            if client:
                db_schema = f"{client}, public, _rrule"

        self.current_path = db_schema
        self.execute(text(f"SET search_path TO {db_schema}"))

    def set_client(self, client: str) -> None:
        if client:
            db_schema = f"{client}, public, _rrule"

            self.current_path = db_schema
            self.execute(text(f"SET search_path TO {db_schema}"))

    @override
    def commit(self):
        super().commit()

        if self.current_path:
            self.execute(text(f"SET search_path TO {self.current_path}"))

    @override
    def rollback(self):
        super().rollback()

        if self.current_path:
            self.execute(text(f"SET search_path TO {self.current_path}"))

@lru_cache
def get_session_maker(connection_id: str):
    engine = PostgresHook(postgres_conn_id=connection_id).get_sqlalchemy_engine()
    return sessionmaker(
        bind=engine,
        class_=ContextSession,
        autoflush=False,
        expire_on_commit=False,
    )

@contextmanager
def get_db_session(connection_id, schema: str|None = None):
    SyncSession = get_session_maker(connection_id)

    with SyncSession() as session:
        session.set_schema(schema=schema)
        yield session

@contextmanager
def get_session(schema: str|None = None, context: AppContext|None = None):
    SyncSession = get_session_maker(getenv('APP__DATABASE__CONN_ID'))

    if not (schema or context):
        context = get_app_context()

    with SyncSession() as session:
        session.set_schema(schema=schema, context=context)
        yield session
