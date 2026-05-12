FORMAT = 'UTF-8'

maps = {"chto": bytearray(550 * 550),"ayth": bytearray(550 * 550),"infe": bytearray(550 * 550),"sorc": bytearray(550 * 550),"lhun": bytearray(550 * 550)}

def _planets():
    planets = [
        "aqua",
        "aegi",
        "lhun",
    ]
    while True:
        for planet in planets:
            yield planet

def _paths():
    points ={
        "aegi": [
            (947, 332,"Frozen Waste"),  
            (850, 633,"2"),  
            (802, 690,"3"),  
            (758, 631,"4"),  
            (703, 698,"5"),  
            (527,664,"fish"),
            (898, 750,"Refugee"),
            (459,703,"Timberbasin"),
            (526,753,"Nighthold"),
        ],"lhun":[
            (248,446),
            (410,245),
            (20,25)
        ],
        "aqua":[
             (479, 441,'13:Mount Siretin'),
             (439, 300,'12:City of Alquarie'),
             (499, 143,'11:Temple of Albila'),
             (434, 124,'10:Chasma Abysnoch'),
             (280, 107,'9:Planitia Scycia'),
             (215, 100,'8:Chasma Tetria'),
             (204, 196,'7:City of Pacipis'),
             (134, 253,'6:Central Basin'),
             (69,  171,'5:City of Soldaran'),
             (67,  280,'4:Chasma Leviara'),
             (79,  429,'3:Sunken Outpost'),
             (174, 332,'2:Citadel of Pearls'),
             (211, 320,'1:Nautheas Basin'),
        ],

    }
    while True:
        prev = planet
        for point in points[planet]:
            if prev != planet:
                print("break")
                break
            yield point


        

planet_g = _planets()
coords_g = _paths()

planet,goto_xy = None,None

def cycle_planet():
    global planet
    planet = next(planet_g)
    return planet
def cycle_points():
    global goto_xy
    goto_xy = next(coords_g)
    return goto_xy


cycle_planet()
cycle_points()


def _cycle_iris():
    data = [
        2,1,1,2,3,3,1,4,1,3,2,2,4,4,4,3,2,1,2,4,2,2,3,2,4,2,3,4,1,2,3,1,3,3,4,4,
        1,2,1,3,3,3,3,4,1,4,2,3,2,3,4,3,2,4,4,2,4,2,4,4,1,3,3,1,3,1,4,4,3,4,4,3,
        1,1,2,4,4,3,3,3,2,1,4,4,2,2,1,3,2,3,3,3,1,2,1,2,3,4,4,4,1,4,3,4,3,1,3,4,
        3,4,2,2,2,4,3,3,4,3,3,1,1,4,3,3,2,2,1,4,2,4,3,4,1,1,4,4,4,4,2,3,3,4,2,1,
        2,1,4,3,1,4,3,2,2,3,4,2,3,1,2,4,3,2,3,1,4,2,2,4,2,1,3,4,4,2,1,4,1,1,3,1,
        1,1,2,1,1,3,4,2,4,1,3,4,1,3,1,2,3,2,2,2,3,1,1,3,2,4,3,1,2,2,3,3,2,4,1,1,
        2,2,2,2,1,2,2,4,1,4,1,2,4,1,2,2,1,1,4,2,1,1,1,4,1,4,4,1,1,1,1,3,3,2,3,2,
        1,3,1,3
    ]
    
    while True:
        for i in data:
            yield f"push button {i}"
iris = _cycle_iris()

