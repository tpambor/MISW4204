import os
import re
import datetime
import json
from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
import marshmallow as ma
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from google.cloud import storage
from db import db
from gcp import signing_credentials
from modelos import Task, TaskStatus

blp = Blueprint("Tasks", __name__, description="API para gestionar tareas de conversión de formato")

class TaskInputFilesSchema(ma.Schema):
    fileName = ma.fields.Raw()

class TaskInputFormSchema(ma.Schema):
    newFormat = ma.fields.String(required=True)

    @ma.validates("newFormat")
    def validate_newFormat(self, value):
        if not value.lower() in ('mp4', 'webm', 'avi', 'mpeg', 'wmv'):
            raise ma.ValidationError("Format not supported")

class TaskListParameterSchema(ma.Schema):
    max = ma.fields.Integer(validate=[ma.validate.Range(min=1)])
    order = ma.fields.Integer(validate=[ma.validate.Range(min=0, max=1)])

class TaskSchema(ma.Schema):
    id = ma.fields.Integer()
    created = ma.fields.DateTime()
    status = ma.fields.Enum(TaskStatus)
    fileName = ma.fields.String()
    oldFormat = ma.fields.String()
    newFormat = ma.fields.String()

    @ma.pre_dump(pass_many=False)
    def preprocess(self, data, many, **kwargs):
        if not type(data) is dict:
            new_data = vars(data)
        else:
            new_data = data
        new_data['status'] = TaskStatus(new_data['status'])
        return new_data

class TaskExtendedSchema(TaskSchema):
    urlOriginal = ma.fields.String()
    urlConverted = ma.fields.String()

@blp.route("/api/tasks")
class VistaTasks(MethodView):
    @blp.arguments(TaskInputFilesSchema, location="files")
    @blp.arguments(TaskInputFormSchema, location="form")
    @blp.response(201, TaskSchema)
    @jwt_required()
    def post(self, files, form):
        if not 'fileName' in files:
            abort(422, message="fileName is required")

        filename = files['fileName'].filename.split('.')
        if len(filename) <= 1:
            abort(422, message="Filename must have a extension")

        old_format = filename[-1].lower()
        del filename[-1]
        filename = '.'.join(filename)
        if not re.search(r'^[0-9a-zA-Z][0-9a-zA-Z_\-. ]*$', filename):
            abort(422, message="Invalid filename")

        if not old_format in ('mp4', 'webm', 'avi', 'mpeg', 'wmv'):
            abort(422, message="Format not supported")

        video_content_type = {'mp4': 'video/mp4', 'webm': 'video/webm', 'avi': 'video/x-msvideo', 'mpeg': 'video/mpeg', 'wmv': 'video/x-ms-wmv'}

        new_format = form['newFormat'].lower()

        new_task = Task(
            user = get_jwt_identity(),
            created=datetime.datetime.utcnow(),
            fileName=filename,
            status=TaskStatus.UPLOADED,
            oldFormat=old_format,
            newFormat=new_format,
        )
        db.session.add(new_task)
        db.session.commit()

        storage_client = storage.Client()
        bucket = storage_client.bucket(current_app.config['GCP_BUCKET'])
        blob = bucket.blob(f'{new_task.id}.{old_format}')
        blob.content_disposition = f'attachment; filename={filename}.{old_format}'
        blob.upload_from_file(files['fileName'].stream, content_type=video_content_type[old_format])

        pubsub_task = {
            'id_video': new_task.id,
            'old_format': old_format,
            'new_format': new_format
        }

        future = current_app.extensions["pubsub"].publish(
            current_app.config['PUBSUB_TOPIC'],
            json.dumps(pubsub_task).encode('utf-8')
        )
        future.result()

        return new_task

    @blp.arguments(TaskListParameterSchema, location="query")
    @blp.response(200, TaskSchema(many=True), description="Lista de tareas")
    @jwt_required()
    def get(self, parameters):
        """
        Lista de tareas
        max: Cantidad máxima de tareas a obtener
        order: Orden de las tareas (0: ascendente, 1: descendente)
        """
        # Filtrar y ordenar las tareas de acuerdo a los parametros
        tasks = Task.query.filter_by(user=get_jwt_identity())
        if 'order' in parameters:
            if parameters['order'] == 1:
                # Ordenar de forma descendente si el parametro es 1
                tasks = tasks.order_by(Task.id.desc())
            elif parameters['order'] == 0:
                # Ordenar de forma ascendente si el parametro es 0
                tasks = tasks.order_by(Task.id.asc())
        if 'max' in parameters:
            # Entregar maximo de tareas si el parametro es diferente de None
            tasks = tasks.limit(parameters['max'])
        # Obtener todas las tareas despues de filtrar y ordenar
        tasks = tasks.all()
        return tasks

@blp.route("/api/tasks/<int:id_task>")
class VistaTaskId(MethodView):
    @blp.doc(parameters=[{'name': 'id_task', 'in': 'path', 'description': 'ID de la tarea', 'required': True}])
    @blp.response(200, TaskExtendedSchema(), description="Detalle de la tarea para poder obtener los links de descargar")
    def get(self, id_task):
        """Detalle de una tarea
        
        Consultar el detalle de una tarea y para poder obtener los links de descargar
        """
        verify_jwt_in_request()

        task = Task.query.filter_by(id=id_task).first()

        if not task or task.user != get_jwt_identity():
            abort(404, message="Tarea no encontrada")

        task_data = vars(task)

        creds = signing_credentials()

        storage_client = storage.Client()
        bucket = storage_client.bucket(current_app.config['GCP_BUCKET'])
        blob_old = bucket.blob(f'{task.id}.{task.oldFormat}')

        # Crea las URLs de descarga de archivos
        task_data['urlOriginal'] = blob_old.generate_signed_url(version="v4", credentials=creds, expiration=datetime.timedelta(minutes=15), method="GET")
        if task.status == TaskStatus.PROCESSED:
            blob_new = bucket.blob(f'{task.id}.{task.newFormat}')
            task_data['urlConverted'] = blob_new.generate_signed_url(version="v4", credentials=creds, expiration=datetime.timedelta(minutes=15), method="GET")
        else:
            task_data['urlConverted'] = None

        return task_data

    @blp.doc(parameters=[{'name': 'id_task', 'in': 'path', 'description': 'ID de la tarea', 'required': True}])
    @blp.response(204)
    @blp.response(404, description="Tarea no encontrada")
    @blp.response(422, description="La conversión no ha sido procesada")
    def delete(self, id_task):
        """
        Eliminar una tarea
        Eliminar una tarea siempre y cuando ya haya sido procesada
        @param id_task: ID de la tarea
        """
        verify_jwt_in_request()

        storage_client = storage.Client()
        bucket = storage_client.bucket(current_app.config['GCP_BUCKET'])

        task = Task.query.filter_by(id=id_task).first()
        if task is None or task.user != get_jwt_identity():
            abort(404, message="Tarea no encontrada")
        if task.status != TaskStatus.PROCESSED:
            abort(422, message="La conversión no ha sido procesada")

        blob_old = bucket.blob(f'{task.id}.{task.oldFormat}')
        blob_new = bucket.blob(f'{task.id}.{task.newFormat}')

        db.session.delete(task)
        db.session.commit()

        blob_old.delete()
        blob_new.delete()

        final_message = {
            "code": 204,
            "message": "Tarea eliminada exitosamente",
            "status": "DELETED"
        }
        return final_message
