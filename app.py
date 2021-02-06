import time
import cv2
from flask import Flask, render_template, Response
import json
import pika
from flask_cors import CORS, cross_origin

people_in = 3
people_out = 2

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

connection = pika.BlockingConnection()
channel = connection.channel()

def reset_consumer(ch, method, properties, body):
    global people_in
    global people_out

    people_in = people_out = 0
    diff = 0
    json_payload = json.dumps({'in': people_in, 'out': people_out, 'diff': diff})
    ch.basic_publish(exchange='',
                            routing_key='counter',
                            body=json_payload)

channel.queue_declare(queue='counter')

@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')


def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture('768x576.avi')

    # Read until video is completed
    while(cap.isOpened()):
      # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)

            global people_in
            global people_out

            if (people_in < 10):
                people_in += 1
                diff = people_in - people_out
                print('SENT MQ')
                json_payload = json.dumps({'in': people_in, 'out': people_out, 'diff': diff})
                channel.basic_publish(exchange='',
                            routing_key='counter',
                            body=json_payload)

        else: 
            break
        

@app.route('/video_feed')
@cross_origin()
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""

    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':    
    app.run(debug=True)
    