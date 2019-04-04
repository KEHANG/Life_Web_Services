import os
import sys
import pika

url = os.environ.get('MQ_CONNECTION_URL')
params = pika.URLParameters(url)
params.socket_timeout = int('5') 

def publish_msg(msg, publish_queue):
	connection = pika.BlockingConnection(params)
	channel = connection.channel() 
	channel.queue_declare(queue=publish_queue)
	channel.basic_publish(exchange='',
                      	  routing_key=publish_queue,
                      	  body=msg)

	print("Published msg: '{0}'".format(msg))

if __name__ == '__main__':
	msg = sys.argv[1]
	publish_queue = 'MQ_test'
	publish_msg(msg, publish_queue)