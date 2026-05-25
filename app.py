from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning

# Create SQLAlchemy instance
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.now,nullable=False)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    name = db.Column(db.String(40),nullable=False)
    ects_points = db.Column(db.Integer,nullable=False)

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollment'
    student_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'),primary_key=True)



@app.route('/')
def home():
    return render_template('index.html')

# Run the app and create database
if __name__ == '__main__':
    with app.app_context():  # Needed for DB operations
        db.create_all()      # Creates the database and tables
    app.run(debug=True)
