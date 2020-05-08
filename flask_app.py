
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
#from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
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


app.secret_key = "This is out flask app"
login_manager = LoginManager()
login_manager.init_app(app)


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

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()



## main page
@app.route("/", methods=["GET", "POST"])
def index():
        if request.method == "GET":
            return render_template("welcome.html", error=False)

        user = load_user(request.form["username"])
        if user is None:
            return render_template("welcome.html", error=True)

        if not user.check_password(request.form["password"]):
            return render_template("welcome.html", error=True)

        login_user(user)
        return redirect(url_for('addstudent'))




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

## Menu Options
@app.route("/options")
def options():
        return render_template("options.html")


##delete student

#options
def student_query():
    return Student.query

class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=student_query, allow_blank=False, get_label='FirstName')
    #opts = QuerySelectMultipleField(query_factory=student_query, allow_blank=False, get_label='FirstName')

@app.route('/delete', methods=["GET", "POST"])
def delete():
    form = ChoiceForm()
    if form.validate_on_submit():
        db.session.delete(form.opts.data)
        db.session.commit()
    return render_template('deletestudent.html', form=form)
    return redirect(url_for('index'))







