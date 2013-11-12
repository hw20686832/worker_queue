HOST = 'localhost'
PORT = 7100

DEBUG = False

# RabbitMQ config
RABBITMQ_SERVER = "192.168.2.229"
RABBITMQ_PORT = 5672
RABBITMQ_VHOST = '/dcrawler-pro'
RABBITMQ_USER = 'dcrawler'
RABBITMQ_PASS = '123'
MQ_EXCHANGE = 'processing_exchange'
MQ_INKEY = ''
MQ_INQUEUE = ''
MQ_OUTKEY = 'enroll'
MQ_OUTQUEUE = 'enroll_queue'