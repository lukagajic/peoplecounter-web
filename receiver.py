import pika, sys, os, json

def main():
    connection = pika.BlockingConnection()
    channel = connection.channel()

    channel.queue_declare(queue='counter')

    def callback(ch, method, properties, body):
        people_in = 0
        people_out = 0
        diff = 0
        print(body)
        channel.basic_publish(exchange='',
                                routing_key='counter',
                                body=body)

    channel.basic_consume(queue='counter', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)