import os
import datetime
import pathlib
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as ma
from db import db
from modelos import Task, TaskStatus

blp = Blueprint("Tasks", __name__, description="API para gestionar tareas de conversión de formato")

class TaskInputFilesSchema(ma.Schema):
    fileName = ma.fields.Raw(required=True)

class TaskInputFormSchema(ma.Schema):
    newFormat = ma.fields.String(required=True)

class TaskSchema(ma.Schema):
    id = ma.fields.Integer()
    created = ma.fields.DateTime()
    status = ma.fields.Enum(TaskStatus)
    fileName = ma.fields.String()
    oldFormat = ma.fields.String()
    newFormat = ma.fields.String()

    @ma.pre_dump(pass_many=False)
    def wrap_with_envelope(self, data, many, **kwargs):
        new_data = vars(data)
        new_data['status'] = TaskStatus(new_data['status'])
        return new_data

@blp.route("/api/tasks")
class VistaTasks(MethodView):
    @blp.arguments(TaskInputFilesSchema, location="files")
    @blp.arguments(TaskInputFormSchema, location="form")
    @blp.response(201, TaskSchema)
    def post(self, files, form):
        filename = files['fileName'].filename.split('.')
        old_format = filename[-1].lower()
        del filename[-1]
        filename = '.'.join(filename)
        new_format = form['newFormat'].lower()

        new_task = Task(
            created = datetime.datetime.utcnow(),
            fileName = filename,
            status = TaskStatus.UPLOADED,
            oldFormat = old_format,
            newFormat = new_format,
        )
        db.session.add(new_task)
        db.session.commit()

        video_path = os.path.join(current_app.config['VIDEO_DIR'], f'{new_task.id}.{old_format}')
        files['fileName'].save(video_path)

        celery = current_app.extensions["celery"]
        celery.send_task("convert_video", (
            new_task.id,
            old_format,
            new_format
        ))
        return new_task
