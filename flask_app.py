
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField

app = Flask(__name__, static_url_path='/static')
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

##Student table model
class Student(db.Model):

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(128))
    LastName = db.Column(db.String(128))
    Major = db.Column(db.String(128))
    Email = db.Column(db.String(128))
    MyGrade = db.relationship('Grade', backref='sname', cascade = "all, delete, delete-orphan")

#Assignment Table model
class Assignment(db.Model):

    __tablename__ = "assignment"

    id = db.Column(db.Integer, primary_key=True)
    AssignmentName = db.Column(db.String(128))
    PointsTotal = db.Column(db.Integer)
    AGrade = db.relationship('Grade', backref='assignment', cascade = "all, delete, delete-orphan")

#Grade Table model
class Grade(db.Model):

    __tablename__ = "grade"

    id = db.Column(db.Integer, primary_key=True)
    Assignment_ID = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    Student_ID = db.Column(db.Integer, db.ForeignKey('student.id'))
    Grade = db.Column(db.Float)

#user login table model
class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username

#Managing login credentials
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()


## main page this page shows the login screen
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
        return redirect(url_for('options'))



## code for adding a student
@app.route("/addstudent", methods=["GET", "POST"])
def addstudent():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("addstudent.html")

    newstudent = Student(FirstName=request.form["first"], LastName=request.form["last"], Major=request.form["major"], Email=request.form["email"])
    db.session.add(newstudent)
    db.session.commit()
    return redirect(url_for('roster'))


## add asssignment
@app.route("/addassignment", methods=["GET", "POST"])
def addassignment():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("addassignment.html")



    newassignment = Assignment(AssignmentName=request.form["assname"], PointsTotal=request.form["points"])
    db.session.add(newassignment)
    db.session.commit()
    return redirect(url_for('assignmentlist'))

##asssignment List
@app.route ("/assignmentlist", methods=["GET", "POST"])
def assignmentlist():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("assignmentlist.html", assignmentlist=Assignment.query.all())


## Student roster
@app.route("/roster", methods=["GET", "POST"])
def roster():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("roster.html", roster=Student.query.all())


## Menu Options
@app.route("/options")
def options():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "GET":
        return render_template("options.html")


##delete student

#options
def student_query():
    return Student.query

class ChoiceForm(FlaskForm):
    opts = QuerySelectField(query_factory=student_query, allow_blank=False, get_label='FirstName')


@app.route('/deletestudent', methods=["GET", "POST"])
def delete():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ChoiceForm()
    if form.validate_on_submit():
        db.session.delete(form.opts.data)
        db.session.commit()
        redirect(url_for('roster'))
        return redirect(url_for('roster'))
    return render_template('deletestudent.html', form=form)


##delete assignment
def assignment_query():
    return Assignment.query

class ChoicesForm(FlaskForm):
    opts = QuerySelectField(query_factory=assignment_query, allow_blank=False, get_label='AssignmentName')

@app.route('/deleteassignment', methods=["GET", "POST"])
def deleteassignment():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ChoicesForm()
    if form.validate_on_submit():
        db.session.delete(form.opts.data)
        db.session.commit()
        redirect(url_for('assignmentlist'))
        return redirect(url_for('assignmentlist'))
    return render_template('deleteassignment.html', form=form)


#Logout
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


## Student grades
@app.route('/grade')
def grade():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    sgrade=Grade.query.all()
    return render_template("grade.html", grade=sgrade)

#update student grades
@app.route('/updategrade', methods=["GET", "POST"])
def updategrade():
    if request.method == 'POST':
        mygrade = Grade.query.get(request.form.get('id'))
        mygrade.Grade = request.form['grade']
        db.session.commit()

        return redirect(url_for('grade'))


##search for single student

class singleForm(FlaskForm):
    opts = QuerySelectField(query_factory=assignment_query, allow_blank=False, get_label='AssignmentName')


@app.route('/search', methods=["GET", "POST"])
def search():

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ChoiceForm()
    if form.validate_on_submit():
        return render_template('onesearch.html', one=form.opts.data)
    return render_template('search.html', form=form)








