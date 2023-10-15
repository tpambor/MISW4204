import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL)
session = scoped_session(sessionmaker(engine))

class Base(DeclarativeBase):
    pass
