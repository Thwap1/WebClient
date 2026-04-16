# file containing scripts for database creation and management, so tasks don’t have to be executed manually from the console
import click
from game import app
from extensions import db

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        click.echo("Database initialized")

