import os
from flask import Flask
import flask_smorest
from celery import Celery
from vistas import BlueprintTasks

class CloudConversionToolApi(flask_smorest.Api):
    DEFAULT_ERROR_RESPONSE_NAME = None

def create_app():
    app = Flask(__name__)
    app.config['API_TITLE'] = 'Cloud Conversion Tool API'
    app.config['API_VERSION'] = 'v1'
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

    app.extensions["celery"] = Celery(__name__, broker=os.getenv('BROKER', 'redis://127.0.0.1:6379/0'))

    api = CloudConversionToolApi(app)
    api.register_blueprint(BlueprintTasks)

    return app
