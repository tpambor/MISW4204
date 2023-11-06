from flask import Response
from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("Health Check", __name__)

@blp.route("/health-check")
class VistaHealthCheck(MethodView):
    def get(self):
        return Response("Happy and alive\n", status=200, mimetype='text/plain')
