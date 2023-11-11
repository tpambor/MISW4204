import os
from flask import Flask
import flask_smorest
from celery import Celery
from db import db
from vistas import BlueprintTasks, BlueprintAuth, BlueprintHealth
from flask_jwt_extended import JWTManager

class CloudConversionToolApi(flask_smorest.Api):
    DEFAULT_ERROR_RESPONSE_NAME = None

def create_app():
    app = Flask(__name__)
    app.config['API_TITLE'] = 'Cloud Conversion Tool API'
    app.config['API_VERSION'] = 'v1'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GCP_BUCKET'] = os.getenv('BUCKET', '')
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
        db.create_all()

    app.extensions["celery"] = Celery(__name__, broker=os.getenv('BROKER', 'redis://127.0.0.1:6379/0'))
    app.extensions["celery"].conf.task_send_sent_event = True

    api = CloudConversionToolApi(app)
    api.register_blueprint(BlueprintTasks)
    api.register_blueprint(BlueprintAuth)
    api.register_blueprint(BlueprintHealth)
    jwt = JWTManager(app)

    return app
