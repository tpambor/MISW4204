import csv
import ast
import datetime
import os
import numpy as np
import subprocess
import sys
from google.cloud import pubsub_v1
from concurrent import futures
import json
import threading


lock = threading.Lock()

csv_filename = 'output.csv'
data = {}
time_per_request = []
sent_per_request = []
time_request_avg = 0
initial_time = 0
completed_time = 0

NUM_PARALLEL_TASKS = os.getenv('NUM_PARALLEL_TASKS')
NUM_CYCLES = os.getenv('NUM_CYCLES')
PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC')
PUBSUB_MONITOR_SUBSCRIPTION = os.getenv('PUBSUB_MONITOR_SUBSCRIPTION')
PUBSUB_COMPLETION_MONITOR_SUBSCRIPTION = os.getenv('PUBSUB_COMPLETION_MONITOR_SUBSCRIPTION')

def message_received_callback(message):
    global initial_time
    message_json = json.loads(message.data)
    print(f"Petición de conversion enviada: {message_json}", flush=True)
    id_video = message_json['id_video']
    sent = message_json['task_sent']
    with lock:
        if len(data) == 0:
            initial_time = datetime.datetime.fromisoformat(sent)
        if id_video in data:
            data[id_video]['sent'] = sent
        else:
            data[id_video] = {'id_video': id_video, 'sent': sent, 'finished': None, 'time_request': None}

    time_request_calc(id_video)

    message.ack()

def completion_message_received_callback(message):
    message_json = json.loads(message.data)
    print(f"Petición de conversion finalizada: {message_json}", flush=True)

    id_video = message_json['task_id']
    finished = message_json['task_completed']
    with lock:
        if id_video in data:
            data[id_video]['finished'] = finished
        else:
            data[id_video] = {'id_video': id_video, 'sent': None, 'finished': finished, 'time_request': None}

    time_request_calc(id_video)
    
    message.ack()
    

def time_request_calc(id_video):
    global completed_time
    with lock:
        if(data[id_video]['sent'] != None and data[id_video]['finished'] != None):
            sent = datetime.datetime.fromisoformat(data[id_video]['sent'])
            finished = datetime.datetime.fromisoformat(data[id_video]['finished'])
            time_request = (finished - sent).total_seconds() * 1000
            data[id_video]['time_request'] = time_request
            time_per_request.append(time_request)
            write_cvs(id_video)

            if len(time_per_request) == int(NUM_PARALLEL_TASKS)*int(NUM_CYCLES):
                completed_time = finished
                generate_reports()

def write_cvs(id_video):
    with open(csv_filename, mode='a', newline='') as file:
        is_csv_exists = os.path.isfile(csv_filename)
        is_csv_empty = os.stat(csv_filename).st_size == 0

        fieldnames = ['id_video', 'sent', 'finished', 'time_request']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not is_csv_exists or (is_csv_exists and is_csv_empty):
            writer.writeheader()
        writer.writerow(data[id_video])

def generate_reports():
    total_requests = len(time_per_request)
    acum_time_ms = sum(time_per_request)
    total_time_sec = (completed_time - initial_time).total_seconds()
    print(f'total_time_sec', total_time_sec)
    total_time_min = total_time_sec / 60
    print(f'total_time_min', total_time_min)
    sorted_times = sorted(time_per_request)
    percentil_95 = np.percentile(sorted_times, 95)

    report = f"""
-----------------------
Reporte

Total peticiones: {total_requests}
Peticiones concurrentes: {NUM_PARALLEL_TASKS}
Tiempo de respuesta por petición promedio (ms): {acum_time_ms / total_requests:.2f}
Tiempo de respuesta (ms) P95: {percentil_95:.2f}
Peticiones por minuto (Throughput): {total_requests / total_time_min:.2f}
-----------------------
"""
    print(report)

    with open('reporte.txt', 'w') as file:
        file.write(report)
    

    plot_script = f"""
set terminal png size 600
set output "output.png"
set title "{int(NUM_PARALLEL_TASKS)*int(NUM_CYCLES)} peticiones, {NUM_PARALLEL_TASKS} peticiones concurrentes"
set size ratio 0.6
set grid y
set xlabel "Nro Peticiones"
set ylabel "Tiempo de respuesta (ms)"
set datafile separator ","
plot "output.csv" using 4 smooth sbezier
"""
    with open('plot.p', 'w') as file:
        file.write(plot_script)

    subprocess.run("gnuplot plot.p", shell=True, check=True)
    os._exit(0)

def my_monitor():
    print("Comienza monitor")
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        future_a = subscriber.subscribe(PUBSUB_MONITOR_SUBSCRIPTION, message_received_callback)
        future_b = subscriber.subscribe(PUBSUB_COMPLETION_MONITOR_SUBSCRIPTION, completion_message_received_callback)

        try:
            future_a.result()
            future_b.result()
        except KeyboardInterrupt:
            future_a.cancel()
            future_b.cancel()

my_monitor()