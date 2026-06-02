import flask_sqlalchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,EmailField
from wtforms.validators import InputRequired,Length,ValidationError,Email

from datetime import datetime
import enum
import os
import dotenv


app = Flask(__name__)
dotenv.load_dotenv()
# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")
# Create SQLAlchemy instance
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = 'employee'
    GUEST = 'guest'


class User(db.Model,UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),nullable=False,unique=True)
    name = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(320),unique=True)
    surname = db.Column(db.String(30),nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    def __repr__(self):
        return f"id: {self.id} | username: {self.username} | name: {self.name} | surname: {self.surname} | role: {self.role}"
    def get_id(self):
        return self.id
    
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer,unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    name = db.Column(db.String(40),nullable=False)

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime,default=datetime.now,nullable=False)
    datetime_start = db.Column(db.DateTime,nullable=False)
    datetime_end = db.Column(db.DateTime,nullable=False)
    room_id = db.Column(db.Integer,db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accepted = db.Column(db.Boolean,nullable=False,default=False)





class RegisterForm(FlaskForm):
    name = StringField("Name",validators=[])
    surname = StringField("Surname")
    email = EmailField("Email")
    password = PasswordField("Password")
    confirm_password = PasswordField("Confirm Password")
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = EmailField("Email")
    password = PasswordField("Password")
    submit = SubmitField()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    return "login_page"

@app.route('/register')
def register():
    return "Register page"
@app.route('/user')
def user_list():
    return "User List"

# Run the app and create database
if __name__ == '__main__':  # Needed for DB operations
           # Creates the database and tables
    app.run(debug=True)
