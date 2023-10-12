from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint("Tasks", __name__, description="API para gestionar tareas de conversión de formato")

@blp.route("/api/tasks")
class VistaTasks(MethodView):
    def get(self):
        celery = current_app.extensions["celery"]
        celery.send_task("convertir_video", (123, ))
        return "Tarea creado"
