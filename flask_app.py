
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="teamstore20",
    password="gradebook123",
    hostname="teamstore20.mysql.pythonanywhere-services.com",
    databasename="teamstore20$gradebookdb",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(128))
    LastName = db.Column(db.String(128))
    Major = db.Column(db.String(128))
    Email = db.Column(db.String(128))
    MyGrade = db.relationship('Grade', backref='sname')

class Assignment(db.Model):

    __tablename__ = "assignment"

    id = db.Column(db.Integer, primary_key=True)
    AssignmentName = db.Column(db.String(128))
    PointsTotal = db.Column(db.Integer)
    AGrade = db.relationship('Grade', backref='assignment')


class Grade(db.Model):

    __tablename__ = "grade"

    id = db.Column(db.Integer, primary_key=True)
    Assignment_ID = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    Student_ID = db.Column(db.Integer, db.ForeignKey('student.id'))
    Grade = db.Column(db.Float)

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

## main page
@app.route("/", methods=["GET", "POST"])
def index():
        return render_template("welcome.html")

## code for adding a student
@app.route("/addstudent", methods=["GET", "POST"])
def addstudent():
    if request.method == "GET":
        return render_template("addstudent.html")

    newstudent = Student(FirstName=request.form["first"], LastName=request.form["last"], Major=request.form["major"], Email=request.form["email"])
    db.session.add(newstudent)
    db.session.commit()
    return redirect(url_for('index'))

## Student roster
@app.route("/roster", methods=["GET", "POST"])
def roster():
        return render_template("roster.html", roster=Student.query.all())






