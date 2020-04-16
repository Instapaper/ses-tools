from __future__ import absolute_import
from __future__ import print_function

from boto import sqs
import json
import signal
import sys
import traceback

from workers import sqs_tasks

def process_messages(queue, handler, num_messages=10, wait_time_seconds=20):
    messages = queue.get_messages(num_messages=num_messages, wait_time_seconds=wait_time_seconds)
    for message in messages:
        try:
            data = json.loads(message.get_body())
        except ValueError:
            print('[SQS %s] Message did not contain JSON: %s' % (queue.name, message.get_body()))
            queue.delete_message(message)
            continue

        try:
            handler(data)
            queue.delete_message(message)
        except Exception, e:
            formatted_exception = traceback.format_exception(*sys.exc_info())
            print('[SQS %s] Handler error: %s\n%s\n' % (queue.name, formatted_exception, message.get_body()))

def shutdown(signal_num, frame):
    sig = 'UNKNOWN'
    if signal_num == 2:
        sig = 'SIGINT'
    elif signal_num == 15:
        sig = 'SIGTERM'
    print('\n[SQS Worker] Shutting down: %s' % sig)
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <region> <queue-name>' % sys.argv[0])
        sys.exit(-1)

    print('[SQS Worker] Starting up...')
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    region = sys.argv[1]
    connection = sqs.connect_to_region(region)
    if not connection:
	    print('[SQS Worker] Failed to connect to region %s' % region)
	    sys.exit(-1)
 
    queue_name = sys.argv[2]
    try:
        handler = getattr(sqs_tasks, queue_name)
    except Exception, e:
        print('[SQS Worker] No handler exists for queue: %s' % queue_name)
        sys.exit(-1)

    try:
        queue = connection.get_queue(queue_name)
        if queue == None:
            raise ValueError('Unable to connect to queue')
    except Exception, e:
        print('[SQS Worker] Error connecting to queue %s: %s' % (queue_name, str(e)))
        sys.exit(-1)

    print('[SQS Worker] Started for queue %s' % queue_name)
    while True:
        try:
            process_messages(queue, handler)
        except Exception, e:
            print('[SQS Worker] Error in queue runloop: %s' % str(e))
