const { Logging } = require('@google-cloud/logging');
const fs = require('fs');
const { execSync } = require('child_process');

const logging = new Logging();

const NUM_PARALLEL_TASKS = process.env.NUM_PARALLEL_TASKS;
const NUM_CYCLES = process.env.NUM_CYCLES;

const timePerRequest = []
const sentPerRequest = []
const completedPerRequest = []


let TASKS_MAX;
if ((typeof NUM_PARALLEL_TASKS !== 'undefined') && (typeof NUM_CYCLES !== 'undefined')) {
    TASKS_MAX = NUM_PARALLEL_TASKS * NUM_CYCLES;
}

let tasks_finished = 0;

var csvStream = fs.createWriteStream('output.csv');

csvStream.write('id_video,sent,finished,time_request\n')

const calculatePercentile = (arr, percentile) => {
    const index = Math.ceil((percentile / 100) * arr.length) - 1;
    return arr[index];
};

const generateReports = () => {
    const initialTime = sentPerRequest.slice().sort()[0];
    const completedTime = completedPerRequest.slice().sort((a, b) => b - a)[0];
    console.log('initialTime', initialTime);
    console.log('completedTime', completedTime);

    const totalRequests = timePerRequest.length;
    const acumTimeMs = timePerRequest.reduce((acc, time) => acc + time, 0);
    const totalSeconds = (completedTime - initialTime) / 1000;
    const totalTimeMin = totalSeconds / 60;
    console.log('totalSeconds', totalSeconds);
    console.log('totalTimeMin', totalTimeMin);

    const sortedTimes = timePerRequest.slice().sort((a, b) => a - b);
    const percentil95 = calculatePercentile(sortedTimes, 95);

    const report = `
-----------------------
Report

Total requests: ${totalRequests}
Concurrent requests: ${NUM_PARALLEL_TASKS}
Average response time per request (ms): ${(acumTimeMs / totalRequests).toFixed(2)}
Response time (ms) P95: ${percentil95.toFixed(2)}
Requests per minute (Throughput): ${(totalRequests / totalTimeMin).toFixed(2)}
-----------------------
`;
    console.log(report);

    const reportFile = 'reporte.txt';

    try {
        fs.writeFileSync(reportFile, report, 'utf-8');
        console.log(`Archivo "${reportFile}" creado con éxito.`);
    } catch (error) {
        console.error(`Error al escribir el archivo "${reportFile}":`, error);
    }

    const plotScript = `
set terminal png size 600
set output "output.png"
set title "${parseInt(NUM_PARALLEL_TASKS) * parseInt(NUM_CYCLES)} requests, ${NUM_PARALLEL_TASKS} concurrent requests"
set size ratio 0.6
set grid y
set xlabel "Request Number"
set ylabel "Response Time (ms)"
set datafile separator ","
plot "output.csv" using 4 smooth sbezier
`;

    const plotFile = 'plot.p';

    try {
        fs.writeFileSync(plotFile, plotScript, 'utf-8');
        console.log(`Archivo "${plotFile}" creado con éxito.`);
    } catch (error) {
        console.error(`Error al escribir el archivo "${plotFile}":`, error);
    }

    try {
        execSync('gnuplot plot.p', { stdio: 'inherit' });
        console.log('Comando gnuplot ejecutado con éxito.');
    } catch (error) {
        console.error('Error al ejecutar el comando gnuplot:', error.message);
    }

    return
};


const stream = logging
  .tailEntries({
    filter: 'resource.labels.service_name="converter-worker" AND jsonPayload.message="Video conversion task completed"',
  })
  .on('error', console.error)
  .on('data', resp => {
    resp.entries.forEach((entry) => {
        const task = entry.data

        csvStream.write(`${task.video_id},${task.publish_time},${task.completion_time},${task.processing_time}\n`);

        console.log(task)

        sentPerRequest.push(task.publish_time)
        timePerRequest.push(task.processing_time)
        completedPerRequest.push(task.completion_time)

        tasks_finished++;
        if (tasks_finished >= TASKS_MAX)
            return;
    });

    if (tasks_finished >= TASKS_MAX)
        stream.end();
  })
  .on('end', () => {
    csvStream.end()
    console.log('Stream has ended');
    generateReports()
  });
