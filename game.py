from flask import Flask, render_template, request
from flask_socketio import SocketIO
from extensions import GMCP
import threading
import socket
import asyncio
from models import Dawae, Rooms
import logging
import roominfo
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

# --- browser connects.
@socketio.on('connect')
def handle_connect():
    asyncio.run_coroutine_threadsafe(mud_session(request.sid),mud_loop)

async def send_msg(msg, sid):
    try:
        writer = mud_connections[sid]['writer']
        writer.write((msg+"\n").encode(FORMAT))
        await writer.drain()
    except Exception as e:
        print("error while trying to send data to mud:",e)
    

@socketio.on('msg')
def msg(data):
    sid = request.sid
    if sid in mud_connections:
        if data["msg"]:
            asyncio.run_coroutine_threadsafe(send_msg(data["msg"],sid),mud_loop)


async def mud_session(sid):
    reader, writer = await asyncio.open_connection(ICEHOST, ICEPORT)
    await process_session(sid, reader, writer)

async def process_session(sid,reader,writer):
    mud_connections[sid] = {"reader": reader,"writer": writer}
    
    await GMCP.gmcp_order(writer)
    
    STATE_OUTPUT,STATE_IAC, STATE_IAC_2, STATE_GMCP, STATE_GMCP_PREV_WAS_IAC  = 0,1,2,3,4
    state = STATE_OUTPUT

    text_buffer = bytearray() 
    gmcp_buffer = bytearray()
    output=""
    
    while True:
        og_data=b""
        while True:
            try:
                
                #first will try to get much output/other information there parsed inside python before to browser
                newline_index = text_buffer.find(b'\n')
                
                if newline_index != -1:
                    og_data = text_buffer[:newline_index]
                    del text_buffer[:newline_index + 1]
                    og_data+=b'\n'
                    #outerloop will handle data and prevent too much nesting.
                    break 
                if output:
                    #should put everyting here at once.
                    socketio.emit('output',{'output':output},to=sid)
                output = ""
                chunk = await asyncio.wait_for(reader.read(2048), timeout=0.25)
                if not chunk:
                    raise asyncio.CancelledError
                
                for b in chunk:
                    if state == STATE_OUTPUT:
                        if b == 0xFF:
                           print("IAC")
                           state = STATE_IAC
                        else:
                           text_buffer.append(b)
                    elif state == STATE_IAC:
                        if b == 0xFA:
                           state = STATE_GMCP
                        elif b in (0xFB, 0xFC, 0xFD, 0xFE): # WILL/WONT/DO/DONT → 3-byte
                           state = STATE_IAC_2
                        elif b in (0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xF0):# 2-byte IAC commands → just skip
                           state = STATE_OUTPUT
                        else:
                           print("something possibly went wrong with happened parsing telnet.")
                    elif state == STATE_IAC_2:
                       state = STATE_OUTPUT
                    elif state == STATE_GMCP:
                       gmcp_buffer.append(b)
                       if b ==  0xFF:
                           state = STATE_GMCP_PREV_WAS_IAC
                    elif state == STATE_GMCP_PREV_WAS_IAC:
                       gmcp_buffer.append(b)
                       if b == 0xF0:
                           if gmcp_buffer.startswith(b'\xc9Party.Info'):
                               pass #TODO (statuswindow)
                           elif gmcp_buffer.startswith(b'\xc9Room.Info'):
                               ui_keys, room, hero = roominfo.parseRoomInfo(gmcp_buffer[11:-2])
                               pass #TODO (mapper, fastkeys etc)
                           state = STATE_OUTPUT
                           gmcp_buffer.clear()
                       elif b ==  0xFF:
                           state = STATE_GMCP_PREV_WAS_IAC 
                       else:
                           state = STATE_GMCP
                
            # timeout happens if no messages from mud, and since parcing happens only at end of line commands this will flush all not \n terminated in a bit.
            # (assumption that if went to timeout, there is no telnet signals inside of it.)
            except asyncio.TimeoutError:
                if text_buffer:
                    og_data = bytes(text_buffer)
                    text_buffer.clear()
                    break
            except Exception as e:
                print("connection error:",e)
        
        data = og_data.decode(FORMAT, errors='ignore')
        output+=data
        
    

@app.route("/")
def index():
    client_ip = request.remote_addr
    if client_ip == HOST or client_ip.startswith('192'):
        return render_template("index.jinja", fog="true", admin = "true")
    return ""


if __name__ == '__main__':
    with app.app_context():     
        socketio.run(app, log_output=False, debug=False, host=HOST, port=int("80"))



