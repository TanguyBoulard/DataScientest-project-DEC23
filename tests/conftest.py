import pytest

from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData, create_engine, text, inspect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from app.models.database import Base, SessionLocal, engine


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    users = Table('user', Base.metadata,
                  Column('id', Integer, primary_key=True),
                  Column('username', String),
                  Column('password', String),
                  Column('email', String)
                  )

    Base.metadata.create_all(bind=engine)
    yield db
    db.close()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    for table_name in table_names:
        schemas_table = inspector.get_columns(table_name=table_name)
        foreign_keys = inspector.get_foreign_keys(table_name=table_name)
    Base.metadata.drop_all(bind=engine)


# Fixture pour nettoyer la base de données avant chaque test

def clean_db(db_session):
    # Début de la transaction
    db_session.begin()
    # Nettoyage de toutes les tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    # Validation des changements
    db_session.commit()
    # Fermeture de la transaction
    db_session.close()

# Fixture pour définir la variable d'environnement "ENVIRONMENT" sur "testing" avant chaque test
