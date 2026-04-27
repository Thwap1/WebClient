from game import app
from models import Lhun,Chto,Ayth,Infe,Sorc
import heapq

maps = {"chto": bytearray(550 * 550),"ayth": bytearray(550 * 550),"infe": bytearray(550 * 550),"sorc": bytearray(550 * 550),"lhun": bytearray(550 * 550)}


with app.app_context():
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

                    
def walk_path(start,end,planet):
    global maps
    start=(start[0]-1,start[1])
    end = (end[0]-1,end[1])
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

print(walk_path((30,30),(60,10),"lhun"))