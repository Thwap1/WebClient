# file containing scripts for database creation and management,
# 
import click
from game import app
from extensions import db

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        click.echo("Database initialized")

