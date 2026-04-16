
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from extensions import db
import threading
import socket
import queue
import asyncio
from models import Dawae, Rooms
import logging

#  flask logging config 
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# app setup 
app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
socketio = SocketIO(app)

# (GLOBAL OBJECTS)
mud_connections = {}
player = {}

# constants / network config
FORMAT = 'UTF-8'
ICEHOST = "89.167.95.12"
HEADER = 64000
ICEPORT = 4000

HOST = socket.gethostbyname(socket.gethostname())

# ---- global dedicated asyncio loop thread ---
mud_loop = asyncio.new_event_loop()
def start_mud_loop():
    asyncio.set_event_loop(mud_loop)
    mud_loop.run_forever()
threading.Thread(target=start_mud_loop, daemon=True).start()


@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print("connect:",sid)    
    asyncio.run_coroutine_threadsafe(
        mud_session(sid),
        mud_loop
    )
    
async def mud_session(sid):
    reader, writer = await asyncio.open_connection(ICEHOST, ICEPORT)
    await process_session(sid, reader, writer)

async def process_session(sid,reader,writer):
    mud_connections[sid] = {"reader": reader,"writer": writer}
    
    while True:
        
        chunk = await asyncio.wait_for(reader.read(2048), timeout=0.25)
        if not chunk:
            raise asyncio.CancelledError     
        print(chunk)

@app.route("/")
def index():
    client_ip = request.remote_addr
    if client_ip == HOST or client_ip.startswith('192'):
        return render_template("index.jinja", fog="true", admin = "true")
    return ""


if __name__ == '__main__':
    with app.app_context():     
        socketio.run(app, log_output=False, debug=False, host=HOST, port=int("80"))



