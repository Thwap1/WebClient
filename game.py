
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from extensions import db
from models import Dawae, Rooms

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
socketio = SocketIO(app)
