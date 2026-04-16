import mazeslib
import orjson
import queue
import keybinds
from extensions import db

#global mazes for player
mazes = {}

dictx = {'w' : -1, 'n': 0, 'e': 1, 's': 0, 'd': 0, 'u': 0, 'se':1,'sw':-1,'nw':-1,'ne':1}
dicty = {'w' : 0, 'n': -1, 'e': 0, 's': 1, 'd': 0, 'u': 0, 'se':1,'sw':1,'nw':-1,'ne':-1}
dictz = {'w' : 0, 'n': 0, 'e': 0, 's': 0, 'd': -1, 'u': 1, 'se':0,'sw':0,'nw':0,'ne':0}

dict_dirs = {'west' : 1, 'north': 2, 'east': 4, 'south': 8, 'down': 512, 'up': 256,
          'downstairs': 512, 'upstairs': 256,'se': 2097152,'sw':4194304,'nw':8388608,'ne':16777216,'se,': 2097152,
          'sw,':4194304,'nw,':8388608,'ne,':16777216,'southeast': 2097152,'southwest':4194304,'northwest':8388608,
          'northeast':16777216,'southeast,': 2097152,'southwest,':4194304,'northwest,':8388608,'northeast,':16777216,
          'leave': 1024,'west,' : 1, 'north,': 2, 'east,': 4, 'south,': 8, 'down,': 512, 'up,': 256,  'upstairs,': 256,
          'leave,': 1024,'w' : 1, 'n': 2, 'e': 4, 's': 8, 'd': 512, 'u': 256, 'leave': 1024,
          'w,' : 1, 'n,': 2, 'e,': 4, 's,': 8, 'd,': 512, 'u,': 256,  'upstairs,': 256, 'leave,': 1024}



def poproom(maze):
    try:
        command,dirs = maze['room_queue'].get(timeout=0)
        return (command,dirs)
    except Exception as e:
        return ("","")
        

def parseRoomInfo(data,sid):
    roomdata = orjson.loads(data[11:-2])
    if not "id" in roomdata:
        return (False,False,False)
    
    ui_keys,room,hero = False,False,[]
    id = int(roomdata["id"],16)

    for dict in keybinds.override_dicts:
        if id in keybinds.override_dicts[dict]:
            ui_keys.append(f"{dict} {keybinds.override_dicts[dict][id][0]}")
    print(ui_keys)
    
    if sid not in mazes:
        print("WARNING WARNING! somehow player doesnt have maze!")
        return
    
    maze = mazes[sid]
    if not maze["mapper_state"]:
        return (ui_keys,False,False)

    

    # z = 90 if wondering in ow, and might bump into areas that need to be loaded (load only if not at that area yet)
    if id in mazeslib.bases:
        maze['z'] = 90
        poproom(maze)
        if maze['level_id'] != mazeslib.bases[id]["id"]:
            #setuplevel
            hero = {"x": maze["x"],"y": maze["y"],"z": 90}
        
    elif id in maze["dungeon"]:
        maze["x"] = maze["dungeon"][id]["x"]
        maze["y"] = maze["dungeon"][id]["y"]
        maze["z"] = maze["dungeon"][id]["z"]
        poproom(maze)
    
    if maze["mapper_state"] != "REC":
        return (ui_keys,False,hero)
    
    command,dirs = poproom(maze)
    if maze["prev_id"] in mazeslib.bases:
        if command == mazeslib.bases[maze["prev_id"]]['in_cmd']:
            maze["x"], maze["y"], maze["z"] = 0, 0 ,0
    if maze['z'] != 90:
        for i in dirs:
            if i in dictx:
                maze["x"] += dictx[i]
                maze["y"] += dicty[i]
                maze["z"] += dictz[i]




    return False,False,False