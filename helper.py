# file containing scripts for database creation and management, so tasks don’t have to be executed manually from the console

from game import app, db
if True:
    with app.app_context():
        db.create_all()