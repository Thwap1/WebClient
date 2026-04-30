from game import app
from models import Lhun,Chto,Ayth,Infe,Sorc,Owline
import heapq

from common import maps

def load():
    with app.app_context():
        try:
            width = 550
            for planet in maps:
                mapdb = {"sorc":Sorc,"infe":Infe,"lhun":Lhun,"ayth":Ayth,"chto":Chto}.get(planet)
                rows = mapdb.query.filter(mapdb.map_y.between(0, 529)).all()
                for line in rows:
                    index = 0
                    row = int(line.map_y)*width
                    for char in line.map_rivi:
                        if char in [" ","#","V","^"]:
                            maps[planet][row+index]=1
                        index+=1
            width = 950
            maps['ow'] = bytearray(950*769)

            rows = Owline.query.filter(Owline.map_y.between(228, 997)).all()
            for line in rows:
                index = 0
                row = int(line.map_y-228)*width
                for char in line.map_rivi[:300]:
                        if char in [" ","#","V","^"]:

                            maps['ow'][row+index]=1

                        index+=1
        except Exception as e:
            print("error creating map",e)
                    
def walk_path(start,end,planet):
    global maps
    
    offset_x = -300 if planet == 'aegi' else -1
    offset_y = -228 if planet == 'aegi' else 0

    start=(start[0]+offset_x,start[1]+offset_y)
    end = (end[0]+offset_x,end[1]+offset_y)

    neighbours = {(1,1):'se',(-1,-1):'nw',(1,-1):'ne',(-1,1):'sw',(0, 1):'s', (0, -1):'n', (1, 0):'e', (-1, 0):'w'}
    open_set = []
    heapq.heappush(open_set,(0,start))
    came_from = {start:0}
    came_dir = {start:'l'}
    g_score = {start: 0}
    while open_set:
        heur, current = heapq.heappop(open_set)
        if current == end:
            path = []
            while current != start:
                path.append(came_dir[current])
                current = came_from[current]
            path.reverse()
            return path[:50]
        for dx,dy in neighbours.keys():
            neib = (current[0]+dx,current[1]+dy)
            try:
                if neib in came_from:
                    continue
                came_from[neib] = current
                
                if not maps[planet][(neib[1]*550+neib[0])]:
                    came_dir[neib] = neighbours[dx,dy]
                    g_score[neib]=g_score[current] + 1
                    heapq.heappush(open_set, (g_score[neib]+max(abs(neib[0]-end[0]),abs(neib[1]-end[1])),neib))
            except Exception:
                continue


if 'ow' not in maps:
    load()

