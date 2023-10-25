from celery import Celery
import shutil
import os


NUM_TASKS = int(os.getenv('NUM_TASKS') or 100)
VIDEO_DIR = os.getenv('VIDEO_DIR')
OLD_FORMAT = os.getenv('OLD_FORMAT')
NEW_FORMAT = os.getenv('NEW_FORMAT')
DEMO_VIDEO = os.getenv('DEMO_VIDEO')

celery_app = Celery(__name__, broker=os.getenv('BROKER', 'redis://127.0.0.1:6379/0'))


def publish_tasks(num_tasks):
    for index in range(1, num_tasks + 1):
        try:
            ruta_video_copia = f"{VIDEO_DIR}/{index}.{OLD_FORMAT}"
            shutil.copy(DEMO_VIDEO, ruta_video_copia)
            print(f'Video copiado con éxito como {ruta_video_copia}')
        except Exception as e:
            print(f'Error al copiar el video: {str(e)}')
        args = (index, OLD_FORMAT, NEW_FORMAT)
        celery_app.send_task("convert_video", args)
        print(f"Enviada solicitud {index} a la cola de mensajes.")

if __name__ == "__main__":
    publish_tasks(NUM_TASKS)