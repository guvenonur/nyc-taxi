from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


def postgres_session(params):
    """
    Returns SQLAlchemy session

    :return: session
    :rtype: Session
    """
    host = params.host
    port = params.port
    username = params.username
    password = params.password
    db = params.db

    uri = f'postgresql://{username}:{password}@{host}:{port}/{db}'
    engine = create_engine(uri)

    Session = sessionmaker()
    Session.configure(bind=engine)

    return Session()
