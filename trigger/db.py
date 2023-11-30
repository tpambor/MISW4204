import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from google.cloud.sql.connector import Connector
from google.cloud import storage, pubsub_v1
import google.auth
import pymysql

connector = Connector()

credentials, _ = google.auth.default()
credentials.refresh(request=google.auth.transport.requests.Request())
cloudsql_user = credentials.service_account_email.replace('.gserviceaccount.com', '')
cloudsql_instance = os.getenv('CLOUDSQL_INSTANCE')
cloudsql_db = os.getenv('CLOUDSQL_DB')

# Python Cloud SQL Connector database connection function
def getconn():
    conn = connector.connect(
        cloudsql_instance,
        'pg8000',
        db=cloudsql_db,
        user=cloudsql_user,
        enable_iam_auth=True
    )
    return conn

engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

session = scoped_session(sessionmaker(engine))

class Base(DeclarativeBase):
    pass
