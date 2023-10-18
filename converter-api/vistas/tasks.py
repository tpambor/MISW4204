import os
import datetime
import pathlib
from flask import current_app, send_from_directory, jsonify, url_for, request
from flask.views import MethodView
from flask_smorest import Blueprint
import marshmallow as ma
from flask_jwt_extended import jwt_required
from db import db
from modelos import Task, TaskStatus

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import  request

blp = Blueprint("Tasks", __name__, description="API para gestionar tareas de conversión de formato")

# Ejemplo del resultado de un llamado para obtener el detalle de una tarea para descargar
TaskIdExample = [
    {
        'id': '3',
        'created': '10-10-2023',
        'status': 'PROCESSED',
        'fileName': 'MiCancion',
        'oldFormat': 'MP4',
        'newFormat': 'AVI'
    },
    {
        'id': '5',
        'created': '11-10-2023',
        'status': 'UPLOADED',
        'fileName': 'MiCancion2',
        'oldFormat': 'webm',
        'newFormat': 'mp4'
    }
]
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

    @blp.response(200, TaskSchema(many=True), description="Lista de tareas", example=TaskIdExample)
    @jwt_required()
    def get(self):
        # obtener parametro 'max' de la url
        max_param = request.args.get('max', type=int)
        # obtener parametro 'order' de la url
        order_param = request.args.get('order', type=int)
        # Filtrar y ordenar las tareas de acuerdo a los parametros
        tasks = Task.query
        if order_param is not None:
            if order_param == 1:
                # Ordenar de forma descendente si el parametro es 1
                tasks = tasks.order_by(Task.id.desc())
            elif order_param == 0:
                # Ordenar de forma ascendente si el parametro es 0
                tasks = tasks.order_by(Task.id.asc())
        if max_param is not None:
            # Entregar maximo de tareas si el parametro es diferente de None
            tasks = tasks.limit(max_param)
        # Obtener todas las tareas despues de filtrar y ordenar
        tasks = tasks.all()
        # task = Task.query.all()
        # return task
        return tasks
@blp.route("/api/video/<path:filename>")
class VistaVideo(MethodView):
    def get(self,filename):
        video_dir = current_app.config['VIDEO_DIR']
        original_video_path = os.path.join(video_dir, filename)

        if os.path.exists(original_video_path):
            return send_from_directory(video_dir, filename)

@blp.route("/api/videos")
class VistaVideos(MethodView):
    def get(self):
        video_links = {}

        for video_path in ['1.mp4', '1.webm']:
            video_links[video_path] = url_for('Tasks.VistaVideo', filename=video_path).replace("/api", "")
        
        return jsonify(video_links), 200
    
@blp.route("/api/tasks/<int:id_task>")
class VistaTaskId(MethodView):
    #@jwt_required
    @blp.doc(parameters=[{'name': 'id_task', 'in': 'path', 'description': 'ID de la tarea', 'required': True}])
    @blp.response(200, TaskSchema(), description="Detalle de la tarea para poder obtener los links de descargar", example=TaskIdExample[0])
    def get(self, id_task):
        """Detalle de una tarea
        
        Consultar el detalle de una tarea y para poder obtener los links de descargar
        """
        #user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=id_task).first()
        
        if not task:
            return {"message": "El archivo no fue encontrado"}, 404

        # Crea las URLs de descarga de archivos
        
        #video_dir = current_app.config['VIDEO_DIR']
        
        #  URLs de descarga
        original_video_url = url_for('Tasks.VistaVideo', filename=f'{task.id}.{task.oldFormat}').replace("/api", "")
        new_video_url = url_for('Tasks.VistaVideo', filename=f'{task.id}.{task.newFormat}').replace("/api", "")

      # Diccionario con las URLs
        download_urls = {
            "original_video_url": original_video_url,
            "new_video_url": new_video_url
        }
                    
        return jsonify(download_urls), 200
    
