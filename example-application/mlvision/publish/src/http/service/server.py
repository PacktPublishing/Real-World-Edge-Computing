from flask import Flask
from flask import Response
from flask import render_template
from flask import request

import base64
import json
import os
import requests
import subprocess
import uuid
import threading
import time
import logging

view_cols = int(os.environ['APP_VIEW_COLUMNS'])

admin_html = 'admin1.html' if view_cols == 1 else 'admin.html'
stream_html = 'stream1.html' if view_cols == 1 else 'stream.html'

server = Flask(__name__)

g_stream_frame = None
g_lock = threading.Lock()

def generate_still_wget():
    global g_stream_frame

    if g_stream_frame is not None:
        b64_frame = (base64.b64encode(g_stream_frame)).decode('utf8')
        yield (b64_frame)

def generate_still_test():
    global g_stream_frame

    if g_stream_frame is not None:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + g_stream_frame + b'\r\n')

def generate_stream_MJPEG():
    global g_stream_frame, g_lock

    count = 0
    while True:
        if g_stream_frame is None:
            image_name = 'test-image-' + str(count) + '.jpg'
            image_path = os.path.join('/static', image_name)
            if (count > 4):
                count = 0
            time.sleep(1)
            with open(image_path, "rb") as image:
                frame_read = image.read()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_read + b'\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + g_stream_frame + b'\r\n')

            
# Stream resource url_for. To be called in HTML as <img width="640" heigh="480" src="{{ url_for('stream_video') }}"/>
@server.route('/stream_video')
def stream_video():
    return Response(generate_stream_MJPEG(), mimetype = "multipart/x-mixed-replace; boundary=frame")

# End point for the host as http://<ip-address>:5000/stream 
@server.route('/admin')
def admin():
    return render_template(admin_html)

@server.route('/stream')
def stream():
    return render_template(stream_html)

@server.route('/test')
def test():
    return Response(generate_still_test(), mimetype = "multipart/x-mixed-replace; boundary=frame")

@server.route('/wget')
def test_wget():
    return Response(generate_still_wget(), mimetype = "image/jpeg")

# Default URL http://<ip-address>:5000/
@server.route('/')
def index():
    return render_template('index.html')

# Used by client to publish MJPEG streaming content
@server.route('/publish/stream', methods=['POST'])
def publish_stream():
    global g_stream_frame, g_lock
    if request.headers['Content-Type'] == 'application/json':
        with g_lock:
            g_stream_frame = base64.b64decode(request.json["detect"]["image"])
    return ""

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0')
