const { Logging } = require('@google-cloud/logging');
const fs = require('fs');
const logging = new Logging();

const NUM_PARALLEL_TASKS = process.env.NUM_PARALLEL_TASKS;
const NUM_CYCLES = process.env.NUM_CYCLES;

let TASKS_MAX;
if ((typeof NUM_PARALLEL_TASKS !== 'undefined') && (typeof NUM_CYCLES !== 'undefined')) {
    TASKS_MAX = NUM_PARALLEL_TASKS * NUM_CYCLES;
}

let tasks_finished = 0;

var csvStream = fs.createWriteStream('output.csv');

csvStream.write('id_video,sent,finished,time_request\n')

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
  });
