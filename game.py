from flask import Flask, render_template, request
from flask_socketio import SocketIO
from extensions import GMCP
import threading
import socket
import asyncio
import logging
import alias
import orjson
import mapper
from common import FORMAT
from extensions import db
from mapper import mazes
import keybinds
import importlib
from collections import deque
import re
import trig
m_func = None
if importlib.util.find_spec("extra") is not None:
    from extra import monsterappend
    m_func = monsterappend

   
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


# constants / network config

ICEHOST = "89.167.95.12"
HEADER = 64000
ICEPORT = 4000

HOST = socket.gethostbyname(socket.gethostname())
#
#  global dedicated asyncio loop thread 
#
mud_loop = asyncio.new_event_loop()
def start_mud_loop():
    asyncio.set_event_loop(mud_loop)
    mud_loop.run_forever()
threading.Thread(target=start_mud_loop, daemon=True).start()

ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

@app.route("/")
def index():
    client_ip = request.remote_addr
    if client_ip == HOST or client_ip.startswith('192'):
        return render_template("index.jinja", fog="true", admin = "true")
    return ""

@socketio.on('connect')
def handle_connect():
    asyncio.run_coroutine_threadsafe(mud_session(request.sid),mud_loop)

@socketio.on('disconnect')
def disconnect_disconnect():
    sid = request.sid
    if sid in mud_connections:
        try:
            if sid in mapper.mazes:
                mapper.mazes.pop(sid)
            if sid in mud_connections:
                writer = mud_connections[sid]['writer']
            if writer:
                writer.close()
        except Exception as e:
                print(f"closing connection error: {e}")

#
# Handles incoming client messages from the Socket.IO event 'fkey'.
# checks /alt/ctrl/shift and pics from saved keys what to forward to the 'send_msg'.
# 
@socketio.on('fkey')
def fkey(data):
    sid = request.sid
    if sid in mud_connections:
        if data["fkey"]:
            fkey = data["fkey"]
            if fkey in keybinds.override_dicts and mapper.mazes[sid]["prev_id"] and mapper.mazes[sid]["prev_id"] in keybinds.override_dicts[fkey]:
                for msg in keybinds.override_dicts[fkey][mapper.mazes[sid]["prev_id"]][1:]:   
                     asyncio.run_coroutine_threadsafe(send_msg(sid,msg),mud_loop)
            elif data["ctrl"]:
                if fkey in keybinds.CtrlKeyDownActions:
                    for msg in keybinds.CtrlKeyDownActions[fkey]:
                        asyncio.run_coroutine_threadsafe(send_msg(sid,msg),mud_loop)
            elif data["alt"]:
                if fkey in keybinds.AltKeyDownActions:
                    for msg in keybinds.AltKeyDownActions[fkey]:
                         asyncio.run_coroutine_threadsafe(send_msg(sid,msg),mud_loop)
            elif fkey in keybinds.KeyDownActions:
                for msg in keybinds.KeyDownActions[fkey]:
                   asyncio.run_coroutine_threadsafe(send_msg(sid,msg),mud_loop)

#
# Handles incoming client messages from the Socket.IO event 'msg'.
# Forwards non-empty messages to the 'send_msg'.
# 
@socketio.on('msg')
def msg(data):
    sid = request.sid
    if sid in mud_connections:
        if data["msg"]:
            asyncio.run_coroutine_threadsafe(send_msg(sid,data["msg"]),mud_loop)


#
# Establish and run a single MUD session.
# Opens a TCP connection to the configured MUD server
#    
       
async def mud_session(sid):
    reader, writer = await asyncio.open_connection(ICEHOST, ICEPORT)
    await process_session(sid, reader, writer)

#
#  core loop function responsible for retrieving and processing data from the MUD server
#
async def process_session(sid,reader,writer):
    mud_connections[sid] = {"reader": reader,"writer": writer}
    
    mapper.setup_level(sid,"aegi",socketio)
        
    await GMCP.gmcp_order(writer)
    
    STATE_OUTPUT,STATE_IAC, STATE_IAC_2, STATE_GMCP, STATE_GMCP_PREV_WAS_IAC  = 0,1,2,3,4
    state = STATE_OUTPUT
    partystatus = {}
    text_buffer = bytearray() 
    gmcp_buffer = bytearray()
    output=""
    
    player_pos = None
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
                if output or player_pos or partystatus:
                    
                    if partystatus:
                        socketio.emit('output',{'output':output, 'player_pos': player_pos, 'stat':partystatus,} ,to=sid)
                        partystatus = {} #partystatus without anything would demolish it.
                    else:
                        socketio.emit('output',{'output':output, 'player_pos': player_pos},to=sid)
                output = ""
                player_pos = None
                chunk = await asyncio.wait_for(reader.read(4092), timeout=0.25)
                if not chunk:
                    raise asyncio.CancelledError
                
                for b in chunk:
                    if state == STATE_OUTPUT:
                        if b == 0xFF:
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
                                partydata = orjson.loads(gmcp_buffer[11:-2])
                                partystatus = {}
                                if "members" in partydata:
                                    for m in partydata["members"]:
                                        if m["row"] in [1,2,3]: #not sending offslots (-,-)
                                            partystatus[f"{m["row"]}{m["col"]}"] = [m["hp"],m["sp"],m["ep"]]
                            elif gmcp_buffer.startswith(b'\xc9Room.Info'):
                                
                                try:
                                    mapper.parseRoomInfo(gmcp_buffer[11:-2],sid,socketio)
                                    player_pos = {"x": mapper.mazes[sid]["x"],"y": mapper.mazes[sid]["y"],"z": mapper.mazes[sid]["z"]}
                                    
                                except Exception as e:
                                    print(e)
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
        

        
        

        container = {"og" : og_data}        
        container["text_data"] = ansi_escape.sub('',og_data.decode(FORMAT, errors='ignore').strip())

        if og_data.startswith(b'\033['):
            if (monster := trig.match_color_start(container)):
                
                if sid in mapper.mazes:
                    if "monster" in mapper.mazes[sid]:
                       mapper.mazes[sid]['monster'].append(monster)
                       if m_func:
                           m_func(sid)

        if result:= trig.match_trigger_start_end(container["text_data"]):
            await parse_command(sid,result,container)    
        output += container["og"].decode(FORMAT, errors='ignore')

async def parse_command(sid,initial_commands, data ={}):
    try:
        seen = set()
        stack = deque()

        if not isinstance(initial_commands, list):
            initial_commands = [initial_commands]

        stack.extend(initial_commands)

        while stack:
            comm = stack.popleft()
            if isinstance(comm,list):
                stack.extendleft(reversed(comm))
                continue
            if comm in alias.alias_list:
                if comm not in seen:
                    stack.appendleft(alias.alias_list[comm])
                    seen.add(comm)
                    continue
                
            if comm[0] != "#":
                writer = mud_connections[sid]['writer']
                writer.write((comm+"\n").encode(FORMAT))
                await writer.drain()    
                continue
            if len(comm) < 4:
                continue

            cmd_prefix = comm[1:3].lower()
            #
            # alias
            #
            if cmd_prefix == 'al':
                _,name,*tokens = comm.split()
                if tokens:
                    value = " ".join(tokens)
                elif stack:
                    value = stack.popleft()
                alias.alias_list[name] = value

            #
            # gag
            #
            elif cmd_prefix == 'ga':
                data["og"] = b''
            #
            # nothing

            elif cmd_prefix == 'no':
                pass
            #
            # color

            elif cmd_prefix == "cw":
                if not data:
                    continue
                _,color = comm.split(" ", 1)
                if color and color in trig.COLORS:
                    colored = trig.COLORS[color] + data["text_data"] + trig.COLORS["reset"]+"\n"
                    data["og"] = colored.encode(FORMAT)

            elif cmd_prefix == "ma":
                mapper.handleMovementInterruptions(sid,comm,data["text_data"])
    except Exception as e:
        print("somehow parsing triggers/suff all went wrong")

async def send_msg(sid,msg):
    try:
        if len(msg) == 6 and msg == "RELOAD":
            importlib.reload(alias)
            importlib.reload(keybinds)
            importlib.reload(trig)
            importlib.reload(mapper.mazeslib)
            print("RELOAD")
            return
        if len(msg) == 3 and msg in ['TAL','REC']:
            socketio.emit('output',{'output':mapper.change_state(msg,sid)},to=sid)
            return
        
        wrap = {"msg":msg} 
        if mapper.checkInput(sid, wrap, socketio):
            return

        msg = wrap["msg"]
            
         

        await parse_command(sid,msg)
        
    except Exception as e:
        print("error while trying to send data to mud:",e)



if __name__ == '__main__':
    with app.app_context():     

        
        
        
        
        socketio.run(app, log_output=False, debug=False, host=HOST, port=int("80"))



