import os
from sqlmodel import SQLModel, Session, create_engine

# Em produção (Railway), usa a variável de ambiente DATABASE_URL
# Em desenvolvimento local, usa o SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sistema_academico.db")

# connect_args necessario apenas para SQLite + FastAPI (multithreading)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
