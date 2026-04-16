import mazeslib
import orjson
import queue
import keybinds
from extensions import db
from models import Dawae,Rooms,Lines

#global mazes for player
mazes = {}

# move modifiers to coordinates
dictx = {'w' : -1, 'n': 0, 'e': 1, 's': 0, 'd': 0, 'u': 0, 'se':1,'sw':-1,'nw':-1,'ne':1}
dicty = {'w' : 0, 'n': -1, 'e': 0, 's': 1, 'd': 0, 'u': 0, 'se':1,'sw':1,'nw':-1,'ne':-1}
dictz = {'w' : 0, 'n': 0, 'e': 0, 's': 0, 'd': -1, 'u': 1, 'se':0,'sw':0,'nw':0,'ne':0}

# for calculating rooms actual value (how to draw as svg)
dict_dirs = {'west' : 1, 'north': 2, 'east': 4, 'south': 8, 'down': 512, 'up': 256,
          'downstairs': 512, 'upstairs': 256,'se': 2097152,'sw':4194304,'nw':8388608,'ne':16777216,'se,': 2097152,
          'sw,':4194304,'nw,':8388608,'ne,':16777216,'southeast': 2097152,'southwest':4194304,'northwest':8388608,
          'northeast':16777216,'southeast,': 2097152,'southwest,':4194304,'northwest,':8388608,'northeast,':16777216,
          'leave': 1024,'west,' : 1, 'north,': 2, 'east,': 4, 'south,': 8, 'down,': 512, 'up,': 256,  'upstairs,': 256,
          'leave,': 1024,'w' : 1, 'n': 2, 'e': 4, 's': 8, 'd': 512, 'u': 256, 'leave': 1024,
          'w,' : 1, 'n,': 2, 'e,': 4, 's,': 8, 'd,': 512, 'u,': 256,  'upstairs,': 256, 'leave,': 1024}

default_planet = "aegi"

def change_state(msg,sid):
    if not sid in mazes:
        mazes[sid] = {"room_queue":queue.Queue(),"mapper_state":None, "planet": default_planet }
        
    maze = mazes[sid]
    with maze["room_queue"].mutex:maze["room_queue"].queue.clear()
    maze["mapper_state"] = msg if maze["mapper_state"] == None else None
    if not maze["mapper_state"]:
        return f">> MAPPER OFF >>\n"
    return f">> MAPPER MODE: \033[{36}mTAL\033[0m >>\n" if msg == "TAL" else f">> MAPPER MODE: \033[{31}mREC\033[0m >>\n"

def popRoom(maze):
    try:
        command,dirs = maze['room_queue'].get(timeout=0)
        return (command,dirs)
    except Exception as e:
        return ("","")
        

def parseRoomInfo(data,sid):
    try:
        
        global maze
        roomdata = orjson.loads(data)
        if not "id" in roomdata:
            return (False,False,False,False)
        
        ui_keys= []
        id = int(roomdata["id"],16)
        
        # ---- keybindings from location to UI ---
        for dict in keybinds.override_dicts:
            if id in keybinds.override_dicts[dict]:
                ui_keys.append(f"{dict} {keybinds.override_dicts[dict][id][0]}")

        if sid not in mazes or not mazes[sid]["mapper_state"]:
            return (ui_keys,False,False,False)
        
        maze = mazes[sid]
        # ---- actual locations in map ---
        # z = 90 ow and not inside area.
        hero = False
        dungeon = False
        if id in mazeslib.bases:
            maze['z'] = 90
            popRoom(maze)
            if 'level_id' not in maze or maze['level_id'] != mazeslib.bases[id]["id"]:
                setup_level(sid,maze["planet"],id)
                hero = {"x": maze["x"],"y": maze["y"],"z": 90}
                dungeon = True
        elif id in maze["dungeon"]:
            maze["x"] = maze["dungeon"][id]["x"]
            maze["y"] = maze["dungeon"][id]["y"]
            maze["z"] = maze["dungeon"][id]["z"]
            popRoom(maze)
        if maze["mapper_state"] != "REC":
            return (ui_keys,False,hero,dungeon)
        # ---- generating new rooms to map ---    
        command,dirs = popRoom(maze) #command is 
        if maze["prev_id"] in mazeslib.bases:
            if command == mazeslib.bases[maze["prev_id"]]['in_cmd']:
                maze["x"], maze["y"], maze["z"] = 0, 0 ,0
        if maze['z'] == 90:
            return(ui_keys,False,False,dungeon)
        for i in dirs:
            if i in dictx:
                maze["x"] += dictx[i]
                maze["y"] += dicty[i]
                maze["z"] += dictz[i]

        room_value = sum(dict_dirs.get(exit, 0) for exit in roomdata.get('exits', []))

        
        if maze["autodao"]: # ----- Dao is "way out in some mazes its just easy to bind it to where you came". 
            if (dir_out := {'nw':'se','ne':'sw','se':'nw','sw':'ne','e':'w','w':'e','s':'n','n':'s','u':'d','d':'u'}.get(dirs,None)):
                    maze['da_out'][id] = dir
                    way_out = Dawae(da_nro=-1 , lvl=maze["level_id"],id = id, da_wae = dir_out)
                    db.session.merge(way_out)
        new_room =  Rooms(id = id, lvl = maze["level_id"], x=maze["x"], y=maze["y"], z=maze["z"], value=room_value)
        db.session.merge(new_room)
        db.session.commit()
        hero = {"x": maze["x"],"y": maze["y"],"z": maze["z"]}
        room = {"x":maze["x"],"y":maze["y"],"z":maze["z"],"v":room_value}
        maze["dungeon"][id] = room
        maze["prev_id"] = id
        
        return(ui_keys,hero,room,dungeon)
        
        
    except Exception as e:
        print("room parsing error", e)

def setup_level(sid, new_planet, new_id = -1):
    try:
        global mazes
        if not sid in mazes:
            mazes[sid] = {"room_queue":queue.Queue(),"mapper_state":None, "planet": default_planet }
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

        print(f">> LOADLVL >> {maze["planet"]} : {maze["maze_name"]}:{maze["level_id"]}")
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

    except Exception as error:
        print(f'setup error:{error}')
        print("Error type:", type(error)) 
