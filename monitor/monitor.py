# from celery import Celery
# import ast
# import datetime



# # data = {}

# def my_monitor(app):
#     state = app.events.State()

#     def task_received_handler(event):
#         state.event(event)
#         # task name is sent only with -received event, and state
#         # will keep track of this for us.
#         # task = state.tasks.get(event['uuid'])

#         # id_video = ast.literal_eval(task.info()['args'])[0]
#         print('TASK RECEIVED FOR VIDEO: %s' % (
#            '120',))
        
#         # data[id_video] = {'id_video': id_video, 'received': datetime.datetime.utcnow().isoformat(), 'started': None, 'finished': None}

#     with app.connection() as connection:
#         recv = app.events.Receiver(connection, handlers={
#                 'task-received': task_received_handler,
#                 '*': state.event,
#         })
#         recv.capture(limit=None, timeout=None, wakeup=True)


# app = Celery(broker='redis://redis:6379/0')
# my_monitor(app)

from celery import Celery


def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-received': announce_failed_tasks,
                '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)


app = Celery(broker='redis://redis:6379/0')
my_monitor(app)