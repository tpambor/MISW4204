import csv
import ast
import datetime
import os
import numpy as np
import subprocess
import sys
from google.cloud import pubsub_v1


csv_filename = 'output.csv'
data = {}
time_per_request = []
time_request_avg = 0

NUM_PARALLEL_TASKS = os.getenv('NUM_PARALLEL_TASKS')
NUM_CYCLES = os.getenv('NUM_CYCLES')
PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC')
PUBSUB_SUBSCRIPTION = os.getenv('PUBSUB_SUBSCRIPTION')
PUBSUB_COMPLETION_SUBSCRIPTION = os.getenv('PUBSUB_COMPLETION_SUBSCRIPTION')

def message_received_callback(message):
    print(f"Mensaje recibido de {PUBSUB_SUBSCRIPTION}: {message.data}")
    # Agrega aquí cualquier acción adicional que desees realizar con el mensaje
    message.ack()

def completion_message_received_callback(message):
    print(f"Mensaje recibido de {PUBSUB_COMPLETION_SUBSCRIPTION}: {message.data}")
    # Agrega aquí cualquier acción adicional que desees realizar con el mensaje
    message.ack()

def my_monitor():
    print("Comienza monitor")
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        executor = futures.ThreadPoolExecutor(max_workers = 1)
        scheduler = pubsub_v1.subscriber.scheduler.ThreadScheduler(executor)
        future_a = subscriber.subscribe(PUBSUB_SUBSCRIPTION, message_received_callback, scheduler=scheduler)
        future_b = subscriber.subscribe(PUBSUB_COMPLETION_SUBSCRIPTION, completion_message_received_callback, scheduler=scheduler)

        future_a.result()
        future_b.result()

    # Mantener el script en ejecución
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

my_monitor()

    # def get_id_video(event):
    #     state.event(event)
    #     task = state.tasks.get(event['uuid'])
    #     return ast.literal_eval(task.info()['args'])[0]
    
    # def task_sent_handler(event):
        # id_video =  get_id_video(event)
        # print('TASK SENT FOR VIDEO: %s' % (
        #    id_video,))
        
        # if id_video in data:
        #     data[id_video]['sent'] = datetime.datetime.utcnow().isoformat()
        # else:
        #     data[id_video] = {'id_video': id_video, 'sent': datetime.datetime.utcnow().isoformat(), 'received': None, 'started': None, 'succeeded': None, 'time_request': None}

    # def task_received_handler(event):
    #     id_video =  get_id_video(event)
    #     print('TASK RECEIVED FOR VIDEO: %s' % (
    #        id_video,))
        
    #     if id_video in data:
    #         data[id_video]['received'] = datetime.datetime.utcnow().isoformat()
    #     else:
    #         data[id_video] = {'id_video': id_video, 'sent': None, 'received': datetime.datetime.utcnow().isoformat(), 'started': None, 'succeeded': None, 'time_request': None}

    # def task_started_handler(event):
    #     id_video = get_id_video(event)
    #     print('TASK STARTED FOR VIDEO: %s' % (
    #        id_video,))
        
    #     if id_video in data:
    #         data[id_video]['started'] = datetime.datetime.utcnow().isoformat()
    #     else:
    #         data[id_video] = {'id_video': id_video, 'sent': None, 'received': None, 'started': datetime.datetime.utcnow().isoformat(), 'succeeded': None, 'time_request': None}
        
#     def task_succeeded_handler(event):
#         id_video =  get_id_video(event)
#         print('TASK SUCCEEDED FOR VIDEO: %s' % (
#            id_video,))
        
#         data[id_video]['succeeded'] = datetime.datetime.utcnow().isoformat()

#         sent = datetime.datetime.fromisoformat(data[id_video]['sent'])
#         succedded = datetime.datetime.fromisoformat(data[id_video]['succeeded'])
#         time_request = (succedded - sent).total_seconds() * 1000
        
#         data[id_video]['time_request'] = time_request

#         time_per_request.append(time_request)
        
#         print(data[id_video])

#         with open(csv_filename, mode='a', newline='') as file:
#             is_csv_exists = os.path.isfile(csv_filename)
#             is_csv_empty = os.stat(csv_filename).st_size == 0

#             fieldnames = ['id_video', 'sent', 'received', 'started', 'succeeded', 'time_request']
#             writer = csv.DictWriter(file, fieldnames=fieldnames)
#             if not is_csv_exists or (is_csv_exists and is_csv_empty):
#                 writer.writeheader()
#             writer.writerow(data[id_video])

#         if len(time_per_request) == int(NUM_PARALLEL_TASKS)*int(NUM_CYCLES):
#             total_requests = len(time_per_request)
#             acum_time_ms = sum(time_per_request)
#             total_time_ms = time_per_request[len(time_per_request) - 1]
#             total_time_min = total_time_ms / (1000 * 60)
#             sorted_times = sorted(time_per_request)
#             percentil_95 = np.percentile(sorted_times, 95)

#             report = f"""
# -----------------------
# Reporte

# Total peticiones: {total_requests}
# Peticiones concurrentes: {NUM_PARALLEL_TASKS}
# Tiempo de respuesta por petición promedio (ms): {acum_time_ms / total_requests:.2f}
# Tiempo de respuesta (ms) P95: {percentil_95:.2f}
# Peticiones por minuto (Throughput): {total_requests / total_time_min:.2f}
# -----------------------
# """
#             print(report)

#             with open('reporte.txt', 'w') as file:
#                 file.write(report)

#             plot_script = f"""
# set terminal png size 600
# set output "output.png"
# set title "{int(NUM_PARALLEL_TASKS)*int(NUM_CYCLES)} peticiones, {NUM_PARALLEL_TASKS} peticiones concurrentes"
# set size ratio 0.6
# set grid y
# set xlabel "Nro Peticiones"
# set ylabel "Tiempo de respuesta (ms)"
# set datafile separator ","
# plot "output.csv" using 6 smooth sbezier
# """

#             with open('plot.p', 'w') as file:
#                 file.write(plot_script)

#             subprocess.run("gnuplot plot.p", shell=True, check=True)
            
#             sys.exit()