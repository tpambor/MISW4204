from celery import Celery
import csv
import ast
import datetime
import os

csv_filename = 'data.csv'
data = {}

BROKER = os.getenv('BROKER')

def my_monitor(app):
    state = app.events.State()

    def get_id_video(event):
        state.event(event)
        task = state.tasks.get(event['uuid'])
        return ast.literal_eval(task.info()['args'])[0]
    
    def task_sent_handler(event):
        id_video =  get_id_video(event)
        print('TASK SENT FOR VIDEO: %s' % (
           id_video,))
        
        if id_video in data:
            data[id_video]['sent'] = datetime.datetime.utcnow().isoformat()
        else:
            data[id_video] = {'id_video': id_video, 'sent': datetime.datetime.utcnow().isoformat(), 'received': None, 'started': None, 'succeeded': None, 'time_request': None}

    def task_received_handler(event):
        id_video =  get_id_video(event)
        print('TASK RECEIVED FOR VIDEO: %s' % (
           id_video,))
        
        if id_video in data:
            data[id_video]['received'] = datetime.datetime.utcnow().isoformat()
        else:
            data[id_video] = {'id_video': id_video, 'sent': None, 'received': datetime.datetime.utcnow().isoformat(), 'started': None, 'succeeded': None, 'time_request': None}

    def task_started_handler(event):
        id_video = get_id_video(event)
        print('TASK STARTED FOR VIDEO: %s' % (
           id_video,))
        
        if id_video in data:
            data[id_video]['started'] = datetime.datetime.utcnow().isoformat()
        else:
            data[id_video] = {'id_video': id_video, 'sent': None, 'received': None, 'started': datetime.datetime.utcnow().isoformat(), 'succeeded': None, 'time_request': None}
        
    def task_succeeded_handler(event):
        id_video =  get_id_video(event)
        print('TASK SUCCEEDED FOR VIDEO: %s' % (
           id_video,))
        
        data[id_video]['succeeded'] = datetime.datetime.utcnow().isoformat()

        sent = datetime.datetime.fromisoformat(data[id_video]['sent'])
        succedded = datetime.datetime.fromisoformat(data[id_video]['succeeded'])
        time_request = (succedded - sent).total_seconds() * 1000
        
        data[id_video]['time_request'] = time_request
        
        print(data[id_video])

        

        with open(csv_filename, mode='a', newline='') as file:
            # Comprueba si el archivo CSV ya existe
            is_csv_exists = os.path.isfile(csv_filename)

            # Comprueba si el archivo CSV está vacío
            is_csv_empty = os.stat(csv_filename).st_size == 0
            fieldnames = ['id_video', 'sent', 'received', 'started', 'succeeded', 'time_request (ms)']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not is_csv_exists or (is_csv_exists and is_csv_empty):
                writer.writeheader()
            writer.writerow(data[id_video])

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-sent': task_sent_handler,                
                'task-received': task_received_handler,
                'task-started': task_started_handler,
                'task-succeeded': task_succeeded_handler,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)


app = Celery(broker=BROKER)


my_monitor(app)
