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
                        if char in ['#',"V","c"," ","^","~","R"]:
                            maps[planet][row+index]=1
                        index+=1
            width = 1500
            maps['aegi'] = bytearray(width*1200)

            rows = Owline.query.filter(Owline.map_y.between(0, 997)).all()
            for line in rows:
                
                index = 0
                
                row = int(line.map_y)*width
                
                for c in line.map_rivi:
                    
                    if c in {'#',"V","c"," ","^","~","R"}:
                        
                        maps['aegi'][row+index]=1

                    
                    index+=1
                

        except Exception as e:
            print("error creating map",e)




def walk_path(start,end,planet):
    global maps
    
    
    p_width = 1500 if planet == 'aegi' else 550
    start=(start[0],start[1])
    end = (end[0],end[1])
    print(start,end,p_width)
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
            if current[0] > p_width or current[0] < 0 or current[1] < 0:

                continue
            try:
                if neib in came_from:
                    continue
                came_from[neib] = current
                
                if not maps[planet][(neib[1]*p_width+neib[0])]:
                    
                    came_dir[neib] = neighbours[dx,dy]
                    g_score[neib]=g_score[current] + 1
                    heapq.heappush(open_set, (g_score[neib]+max(abs(neib[0]-end[0]),abs(neib[1]-end[1])),neib))
            except Exception:
                continue

def echo_test_location(x,y):
    txt = ""
    
    for y_ in range (y-10,y+10):
        for x_ in range (x-10,x+10):
            if x_ == x and y_ == y:
                txt+="@"
            else:
                txt+=  str(maps['aegi'][y_*1500+x_])
        txt+='\n'
    print(txt)

    

if 'aegi' not in maps:
    load()


