import datetime
from . import db
from werkzeug.security import generate_password_hash
        
attendees = db.Table('event_attendees_asc',
  db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
  db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

user_groups = db.Table('user_groups',
db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = "users"
  
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False)
  
    def __init__(self, firstname, lastname, email, password):
      self.firstname = firstname
      self.lastname = lastname
      self.email = email
      self.password = generate_password_hash(password, method='pbkdf2:sha256')
      self.points = 0
   
    def __repr__(self):
      return f"<User {self.firstname}>"


class Event(db.Model):
  __tablename__ = "events"

  id = db.Column(db.Integer, primary_key=True)
  image = db.Column(db.String(255), nullable=False)
  title = db.Column(db.String(120), nullable=False, unique=True)
  location = db.Column(db.String(255), nullable=False, unique=True)
  manpower_quota = db.Column(db.Integer, nullable=False)
  attendees = db.relationship('User', secondary='event_attendees_asc', passive_deletes=True, lazy=True)
  date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

  def __init__(self, image, title, location, manpower_quota):
    self.image = image
    self.title = title
    self.location = location
    self.manpower_quota = manpower_quota


  
  class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=datetime.datetime.utcnow())
    members = db.relationship('User', secondary='user_groups', lazy=True,
      backref=db.backref('groups'))
  
    def __init__(self, name):
      self.name = name
  
    def __repr__(self):
      return f"<Group {name}>"