import json
import pika

from .app import app

rmq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=app.config['RMQ_HOST']))
channel = rmq_connection.channel()


def rmq_push_to_queue(queue, msg):
    channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
      )
    )

def rmq_pull_from_queue(queue):
    method_frame, header_frame, body = channel.basic_get(queue)

    if method_frame:
        return json.loads(body)
    else:
        return None


def rmq_delete_queue(queue):
    channel.queue_delete(queue=queue)


def rmq_queue_length(queue):
    q = channel.queue_declare(queue=queue, durable=True)

    return q.method.message_count