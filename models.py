import enum
from datetime import datetime
from flask_login import UserMixin
from extensions import db

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = 'employee'
    GUEST = 'guest'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(320), unique=True)
    surname = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    banned = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"id: {self.id} | username: {self.username} | role: {self.role} | banned: {self.banned}"

    def get_id(self):
        return str(self.id)


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(40), nullable=False)


class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now, nullable=False)
    datetime_start = db.Column(db.DateTime, nullable=False)
    datetime_end = db.Column(db.DateTime, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    room = db.relationship('Room', backref='room_reservations')
    user = db.relationship('User', backref='user_reservations')