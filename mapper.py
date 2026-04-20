import mazeslib
import orjson
import queue
import keybinds
from extensions import db
import re
from models import Dawae,Rooms,Lines

#global mazes for player(s)
mazes = {}


dictx = {'w' : -1, 'n': 0, 'e': 1, 's': 0, 'd': 0, 'u': 0, 'se':1,'sw':-1,'nw':-1,'ne':1}
dicty = {'w' : 0, 'n': -1, 'e': 0, 's': 1, 'd': 0, 'u': 0, 'se':1,'sw':1,'nw':-1,'ne':-1}
dictz = {'w' : 0, 'n': 0, 'e': 0, 's': 0, 'd': -1, 'u': 1, 'se':0,'sw':0,'nw':0,'ne':0}
default_planet = "aegi"
dict_dirs = {'west' : 1, 'north': 2, 'east': 4, 'south': 8, 'down': 512, 'up': 256,
          'downstairs': 512, 'upstairs': 256,'se': 2097152,'sw':4194304,'nw':8388608,'ne':16777216,'se,': 2097152,
          'sw,':4194304,'nw,':8388608,'ne,':16777216,'southeast': 2097152,'southwest':4194304,'northwest':8388608,
          'northeast':16777216,'southeast,': 2097152,'southwest,':4194304,'northwest,':8388608,'northeast,':16777216,
          'leave': 1024,'west,' : 1, 'north,': 2, 'east,': 4, 'south,': 8, 'down,': 512, 'up,': 256,  'upstairs,': 256,
          'leave,': 1024,'w' : 1, 'n': 2, 'e': 4, 's': 8, 'd': 512, 'u': 256, 'leave': 1024,
          'w,' : 1, 'n,': 2, 'e,': 4, 's,': 8, 'd,': 512, 'u,': 256,  'upstairs,': 256, 'leave,': 1024}



#
#   is mapper recording, following or off
#

def change_state(msg,sid):
    if not sid in mazes:
        mazes[sid] = {"room_queue":queue.Queue(),"mapper_state":None, "planet": default_planet, "had_keys": False, "prev_id": None, 'dae_lvl': 0, 'dae_default': 0}
    
    maze = mazes[sid]
    maze['wait_dae'] = 0
    with maze["room_queue"].mutex:maze["room_queue"].queue.clear()
    maze["mapper_state"] = msg if maze["mapper_state"] == None else None
    if not maze["mapper_state"]:
        return f">> MAPPER OFF >>\n"
    return f">> MAPPER MODE: \033[{36}mTAL\033[0m >>\n" if msg == "TAL" else f">> MAPPER MODE: \033[{31}mREC\033[0m >>\n"

#
#   helper / first room out from queue to handle
#
def popRoom(maze):
    try:
        command,dirs = maze['room_queue'].get(timeout=0)
        return (command,dirs)
    except Exception as e:
        print(e)
        return ("","")
        
#
#   parse roominfo.gmcppacket
#
def parseRoomInfo(data,sid,socketio):
    try:
        
        global maze
        roomdata = orjson.loads(data)
        if not "id" in roomdata or sid not in mazes:
            return False
        
        maze = mazes[sid]
        ui_keys= []
        maze['monster'] = []
        maze['wait_dae'] = 0

        prev_id = maze["prev_id"]
        
        new_id = int(roomdata["id"],16)
        maze["prev_id"] = new_id
        print("roomid:",new_id)
        
        
        # ---- keybindings from location to UI ---
        for dict in keybinds.override_dicts:
            if new_id in keybinds.override_dicts[dict]:
                ui_keys.append(f"{dict} {keybinds.override_dicts[dict][new_id][0]}")

        # ---- send / clear keys 
        if ui_keys or maze["had_keys"]:
            socketio.emit('walk_keys',ui_keys,to=sid)

        maze["had_keys"] = True if ui_keys else False
        

        # ---- mapper movement not enabled
        if not mazes[sid]["mapper_state"]:
            return 
        
        
        # ---- actual locations in map ---
        # z = 90 ow and not inside area.
        
        
        if new_id in mazeslib.bases:
            maze['z'] = 90
            popRoom(maze)
            if 'level_id' not in maze or maze['level_id'] != mazeslib.bases[new_id]["id"]:
                setup_level(sid, maze["planet"], socketio, new_id)
                

        #room exists (or not in record mode)        
        elif new_id in maze["dungeon"]:
            maze["x"] = maze["dungeon"][new_id]["x"]
            maze["y"] = maze["dungeon"][new_id]["y"]
            maze["z"] = maze["dungeon"][new_id]["z"]
            popRoom(maze)
            
        
        if maze["mapper_state"] != "REC":
            return
        


        # ---- generating new rooms to map ---    
        command,dirs = popRoom(maze) 
        print(command,dirs)
 
      

        if prev_id in mazeslib.bases:
            if command == mazeslib.bases[prev_id]['in_cmd']:
                maze["x"], maze["y"], maze["z"] = 0, 0 ,0
                
        elif maze['z'] == 90:
            return False
        for i in dirs:
            if i in dictx:
                maze["x"] += dictx[i]
                maze["y"] += dicty[i]
                maze["z"] += dictz[i]  


        room_value = sum(dict_dirs.get(exit, 0) for exit in roomdata.get('exits', []))

        
        if maze["autodao"]: # ----- Dao is "way out in some mazes its just easy to bind it to where you came". 
            if (dir_out := {'nw':'se','ne':'sw','se':'nw','sw':'ne','e':'w','w':'e','s':'n','n':'s','u':'d','d':'u'}.get(dirs,None)):
                    maze['da_out'][new_id] = dir
                    way_out = Dawae(da_nro=-1 , lvl=maze["level_id"],id = new_id, da_wae = dir_out)
                    db.session.merge(way_out)
        
        new_room =  Rooms(id = new_id, lvl = maze["level_id"], x=maze["x"], y=maze["y"], z=maze["z"], value=room_value)
        db.session.merge(new_room)
        db.session.commit()
        
        
        room = {"x":maze["x"],"y":maze["y"],"z":maze["z"],"v":room_value}
        
        socketio.emit('map', {'rooms':[room]}, to = sid)
        maze["dungeon"][new_id] = room
        
        
        
        
    except ValueError as e:
        return
        #room did not have id. might have to return to this so that can map where id is obfuscated
    except Exception as e:
        print("room GMCP mapper.py parsing error", e)

#
#   setup/change level
#
def setup_level(sid, new_planet, socketio, new_id = -1):
    try:
        global mazes
        if not sid in mazes:
            mazes[sid] = {"room_queue":queue.Queue(),"mapper_state":None, "planet": default_planet, "had_keys": False, "prev_id": None, 'dae_lvl': 0, 'dae_default': 0, 'wait_dae': 0 }
        maze = mazes[sid]
        maze['dae_level'] = 0
        maze['dae_default'] = 0
        maze['wait_dae'] = "clear"

        maze['planet'] = new_planet

        if new_id == -1:
            new_id = mazeslib.default[new_planet]
        if new_id in mazeslib.coord_to_id:
            new_id = mazeslib.coord_to_id[new_id]

        if new_id in mazeslib.bases:
            maze["level_id"] = mazeslib.bases[new_id]['id']
            maze["autodao"] = maze["level_id"] in mazeslib.autodao
            maze["maze_name"] = mazeslib.bases[new_id]['name'] 
            maze['x'] = mazeslib.bases[new_id]['x']
            maze['y'] = mazeslib.bases[new_id]['y']
        else:
            maze["level_id"] = 0
            maze["maze_name"] = new_id
        maze['z'] = 90            

        print(f">> LEVEL >> {maze["planet"]} : {maze["maze_name"]}({maze["level_id"]})")
        maze["dungeon"],maze['da_out'],maze["da_wae"] = {},{},{}
        maze['svg_lines']=[]

        for room in Rooms.query.filter_by(lvl = maze["level_id"]):
            maze["dungeon"][room.id] = {'x':room.x, 'y':room.y, 'z':room.z, 'v': room.value}
        for line in Lines.query.filter_by(lvl=maze["level_id"]):
            maze["svg_lines"].append({'x':line.x,'y':line.y,'z':line.z,'x2':line.x2,'y2':line.y2})

        for daw in Dawae.query.filter_by(lvl=maze["level_id"]):
            if daw.da_nro == -1:
                maze["da_out"][daw.id] = daw.da_wae
            else:
                if daw.id not in maze["da_wae"]:
                    maze["da_wae"][daw.id] = [(daw.da_nro,daw.da_wae)]
                else:
                    maze["da_wae"][daw.id].append((daw.da_nro,daw.da_wae))
        socketio.emit('map', {'clear':True,'rooms':list(maze["dungeon"].values()), 'lines':maze["svg_lines"]}, to = sid)
    except Exception as error:
        print(f'setup error:{error}')
        print("Error type:", type(error)) 

#
#   If the mapper is in a state where it is recording input data, that data must be parsed for commands that modify the map and for tracking movement.
#
def checkInput(sid, wrap, socketio):
    msg = wrap["msg"]
    
    global mazes
    if sid not in mazes:
        return False
    maze = mazes[sid]
    
    if msg in ['l','look','glance']:
        maze['monster'] = []
        maze['wait_dae'] = 0

    if not maze['mapper_state']:
        return False
    
    #--- instructions from database to replace normal command. DA_out one layer just to get towards exit
    elif msg == "DA_OUT":

        if maze['z'] == 90 or maze['wait_dae'] == "blocking_out":
            return True
        maze['wait_dae'] = "blocking_out"

        if maze['prev_id'] not in maze['da_out']:
            return True
        
        wrap['msg'] = maze['da_out'][maze['prev_id']]
    
    #--- da_wae is paths inside mazes and always following the current nro path or bigger, if not then search of lower too.
    elif msg == "DA_WAE":            
        if maze['wait_dae'] == "blocking_dae":
            return True
        try:
            maze['wait_dae'] = "blocking_dae"
            way = [x for x in maze["da_wae"][maze["prev_id"]] if x[0]>=maze["dae_lvl"]]
            if not way:
                maze["dae_lvl"] = maze["dae_default"]
                way = [x for x in maze["da_wae"][maze["prev_id"]] if x[0]>=maze["dae_lvl"]]
            if not way:
                return True
            order = min(way,key=lambda x:x[0])
            maze["dae_lvl"],command = order 
            wrap['msg'] = command    
        except Exception as e:
            print("DA_WAE bug",e)
            return True
    
    if maze['mapper_state'] != "REC":
        return
    
    elif msg in ['n','s','e','w','nw','ne','sw','se','u','d']:
        maze["room_queue"].put((msg,msg))

    #--- instructions that the command goes to room_queue, removes the MSK from start.
    elif msg[:3]  == "MSK":
        command,dirs = msg[4:].strip().strip().rsplit(" ", 1)
        maze['room_queue'].put((command,dirs))
        wrap['msg'] = command
    #--- destroy existing maze
    elif msg in ["NUKEMAZE123"]:
        for table in [Rooms,Dawae,Lines]:
            for row in table.query.filter_by(lvl = maze["level_id"]):
                db.session.delete(row)
            db.session.commit()
        setup_level(sid,maze["planet"],socketio,)
        return True
    elif msg[:5] == "LINE " and maze["z"] != 90:
        try:
            dirs = msg[5:]                                                                    
            dx,dy = maze["x"],maze["y"]
            
            for i in dirs:
                if i in dictx:
                    dx += dictx[i]
                    dy += dicty[i]
            newline = {'x':maze["x"],'y':maze['y'],'z':maze['z'],'x2':dx,'y2':dy}
            line = Lines(lvl = maze["level_id"], x=maze["x"], y = maze["y"], z = maze["z"],x2 = dx, y2 = dy)
            db.session.add(line)
            db.session.commit()
            maze["svg_lines"].append(newline)
            socketio.emit('map', {'clear':False, 'lines':[newline]}, to = sid)
            return True
        except Exception as e:
            print("error making svg line:",e)
            return True
    
#
#
def handleMovementInterruptions(sid,command,data):
    
    try:
        global mazes
        if not sid in mazes or not mazes[sid]["mapper_state"] or not mazes[sid]["room_queue"]:
            return
        q = mazes[sid]['room_queue']
        if q.empty():
            return
        if command == "#MAP_1": #remove one
            
            q.get(timeout=0)
        elif command == "#MAP_A": #remove all
            
            with q.mutex:q.queue.clear()
        elif command == "#MAP_F": #keep first remove all others
            first = queue.get(timeout=0)
            with q.mutex:q.queue.clear()
            queue.put(first)
        elif "#MAP_COORDS":
            if re.search(r'^Your current coordinates are x = (\d+), y = (\d+)\.$', data):
                 my_x,my_y = re.findall(r'\b\d+[.,]', data)
                 mazes[sid]['x'],mazes[sid]['y'] = int(my_x[:-1]), int(my_y[:-1])
                 
    except Exception as e:
        print("Error while handling movement interruptions",e)
    