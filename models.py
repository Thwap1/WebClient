from extensions import db

class Owline(db.Model):
    __bind_key__ = 'ae'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}')"
class Chto(db.Model):
    __bind_key__ = 'ch'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}'"
class Infe(db.Model):
    __bind_key__ = 'in'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}'"
class Sorc(db.Model):
    __bind_key__ = 'so'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}'"
class Ayth(db.Model):
    __bind_key__ = 'ay'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}'"
class Lhun(db.Model):
    __bind_key__ = 'lh'
    id = db.Column(db.Integer, primary_key=True)
    map_y = db.Column(db.Integer)
    map_rivi = db.Column(db.String(2000))
    def __repr__(self):
        return f"Line('{self.map_y}, {self.map_rivi}'"
class Rooms(db.Model):
    id,lvl,x,y,z,value = db.Column(db.Integer, primary_key=True),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer)
    def __repr__(self): return f"Rooms({self.lvl}, {self.x}, {self.y}, {self.z}, {self.value})"

class Lines(db.Model):
    id,lvl,x,y,z,x2,y2 = db.Column(db.Integer, primary_key=True),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer),db.Column(db.Integer)
    def __repr__(self): return f"Lines(lvl:{self.lvl}, x:{self.x}, y:{self.y}, z:{self.z}, x2:{self.x2},y2:{self.x2})"

class Dawae(db.Model):
    __bind_key__ = 'da'

    id = db.Column(db.Integer, primary_key=True)
    da_nro = db.Column(db.Integer, primary_key=True)

    lvl = db.Column(db.Integer)
    da_wae = db.Column(db.String)

    def __repr__(self):
        return f"Dawae({self.lvl}, wae_nro:{self.da_nro}, wae:{self.da_wae})"
