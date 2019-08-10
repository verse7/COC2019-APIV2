from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import wtforms_json

app = Flask(__name__)
socketio = SocketIO(app)
csrf = CSRFProtect(app)
cors = CORS(app, resources={r'*': {'origins': '*'}})



csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER'] = './app/static/uploads'
app.config['SECRET_KEY'] = 'v\xf9\xf7\x11\x13\x18\xfaMYp\xed_\xe8\xc9w\x06\x8e\xf0f\xd2\xba\xfd\x8c\xda'
# DATABASE_URL = 'postgresql://admin:password123@localhost/photogram'
DATABASE_URL='postgresql://xcdatgokkmkige:a2030919439e0888d0c95a716a437623b2ae94a97f340aca4e579efdfbf15df0@ec2-54-225-129-101.compute-1.amazonaws.com:5432/d6gj96ea29eaei'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
wtforms_json.init()

from app import views, models
