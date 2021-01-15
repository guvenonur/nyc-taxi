from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


def postgres_engine(params):
    host = params.host
    port = params.port
    username = params.username
    password = params.password
    db = params.db

    uri = f'postgresql://{username}:{password}@{host}:{port}/{db}'
    return create_engine(uri)


def postgres_session(params):
    """
    Returns SQLAlchemy session

    :return: session
    :rtype: Session
    """
    engine = postgres_engine(params)
    Session = sessionmaker()
    Session.configure(bind=engine)

    return Session()
