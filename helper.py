# file containing scripts for database creation and management,
# 

import click
from game import app
from extensions import db
from models import Lhun

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        click.echo("Database initialized")

if False:
    with app.app_context():
        with open("lhun.txt", "r") as f:
            for line in f:   
                if ":::" not in line:
                    continue
                mapnro, mapline = line.split(":::", 1)
                l = Lhun(map_y=mapnro,map_rivi=mapline)
                db.session.add(l)
        db.session.commit()                

