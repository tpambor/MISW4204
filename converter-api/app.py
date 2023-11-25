import os
from flask import Flask
import flask_smorest
import google.auth
from google.cloud import pubsub_v1
from google.cloud.sql.connector import Connector
from db import db
from vistas import BlueprintTasks, BlueprintAuth, BlueprintHealth
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import DatabaseError

class CloudConversionToolApi(flask_smorest.Api):
    DEFAULT_ERROR_RESPONSE_NAME = None

def create_app():
    # Initialize Python Cloud SQL Connector object
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

    app = Flask(__name__)
    app.config['API_TITLE'] = 'Cloud Conversion Tool API'
    app.config['API_VERSION'] = 'v1'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "creator": getconn
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GCP_BUCKET'] = os.getenv('STORAGE_BUCKET')
    app.config['PUBSUB_TOPIC'] = os.getenv('PUBSUB_TOPIC')
    app.config['OPENAPI_VERSION'] = '3.1.0'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['API_SPEC_OPTIONS'] = {
        "components": {
            "securitySchemes": {
                "Bearer Auth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    db.init_app(app)
    with app.app_context():
        retries = 0
        while True:
            try:
                db.create_all()
            except DatabaseError:
                if retries < 5:
                    continue
                else:
                    raise
            break

    app.extensions["pubsub"] = pubsub_v1.PublisherClient()

    api = CloudConversionToolApi(app)
    api.register_blueprint(BlueprintTasks)
    api.register_blueprint(BlueprintAuth)
    api.register_blueprint(BlueprintHealth)
    jwt = JWTManager(app)

    return app
