from flask import Flask, render_template, redirect, request, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key = "i am a secret"

@app.route("/", methods=["GET"])
def register():
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register_user():
    print("=="*80)
    is_valid=True
    if len(request.form['first_name']) <= 0:
        is_valid=False
        flash("First Name is required!")
    if len(request.form["last_name"]) <= 0:
        is_valid=False
        flash("Last Name is required")
    if len(request.form['email']) <= 0:
        is_valid=False
        flash("Email is required!")
    if len(request.form["password"]) <= 0:
        is_valid=False
        flash("Your password is required!")
    if len(request.form['password_confirm']) <= 0:
        is_valid = False
        flash("Password confirmation is required!")
    if not is_valid: 
        return redirect("/")
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        mysql=connectToMySQL("handy_helper")
        query="INSERT INTO users (first_name, last_name, email, password) VALUES (%(fn)s, %(ln)s, %(email)s, %(pw)s);"
        data={
            'fn': request.form['first_name'],
            'ln': request.form['last_name'],
            'email': request.form['email'],
            'pw': pw_hash
        }
        newuser=mysql.query_db(query, data)
        session['id']=newuser
        session['first_name']=request.form['first_name']
        flash("You have been logged in successfully!")
        return redirect("/dashboard")

@app.route("/login", methods=["POST"])
def check_credentials():
    mysql=connectToMySQL("handy_helper")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data ={
        'email': request.form["email"]
    }
    result=mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['id']=result[0]['user_id']
            session['first_name'] = result[0]['first_name']
            flash("You are logged in!")
            return redirect("/dashboard")
        else:
            flash("Please enter credentials to login!")
            db=mysql.query_db(query, data)
            return redirect("/")
    else:
        flash("you are not logged in!")
        return redirect("/")
@app.route("/dashboard",)
def show_jobs_for_loggedin():
    if 'id' in session:
        db = connectToMySQL("handy_helper")
        query = "SELECT * FROM jobs WHERE user_id=%(id)s;"
        data={
            'id': session['id']
        }
        jobs=db.query_db(query, data)
        return render_template("dashboard.html", jobs=jobs)
    else:
        return redirect("/")

@app.route("/create/job", methods=["POST"])
def create_trips():
    print("&"*100)
    is_valid=True
    if len(request.form['title']) <= 4:
        is_valid=False
        flash("Please enter a job title!")
    if len(request.form['description']) <= 4:
        is_valid=False
        flash("Please enter a job description!")
    if len(request.form['location']) <= 2:
        is_valid=False
        flash("Please enter a location!")
    if not is_valid:
        return redirect("/new/job")
    else:
        mysql=connectToMySQL("handy_helper")
        query="INSERT INTO jobs (title, description, location, user_id) VALUES (%(ti)s, %(de)s, %(loc)s, %(id)s);"
        data={
            'ti': request.form['title'],
            'de': request.form['description'],
            'loc': request.form['location'],
            'id': session['id']
        }
        newjob=mysql.query_db(query, data)
        return redirect("/dashboard")

@app.route("/new/job")
def create_a_trip():
    return render_template("job_create.html")

@app.route("/job/show/<id>", methods=["GET"])
def show_selected_trip(id):
    db=connectToMySQL("handy_helper")
    query="SELECT * FROM jobs WHERE job_id=%(id)s;"
    data={
        'id': id
    }
    jobs=db.query_db(query,data)
    print('%'*100)
    print(jobs)
    return render_template("show.html", job=jobs)

@app.route("/job/edit/<id>", methods=["POST"])
def edit_job(id):
    print(request.form)
    is_valid=True
    if len(request.form['title']) <= 4:
        is_valid=False
        flash("Please enter a job title!")
    if len(request.form['description']) <= 4:
        is_valid=False
        flash("Please enter a job description!")
    if len(request.form['location']) <= 3:
        is_valid=False
        flash("Please enter a location!")
    if not is_valid:
        return redirect(f"/job/edit/{id}")
    else:
        mysql=connectToMySQL("handy_helper")
        query= "UPDATE jobs SET title=%(ti)s, description=%(de)s, location=%(loc)s WHERE job_id=%(id)s;"
        data={
            'ti': request.form['title'],
            'de': request.form['description'],
            'loc': request.form['location'],
            'id': id
        }
        jobs=mysql.query_db(query, data)
        return redirect("/dashboard")

@app.route("/job/edit/<id>", methods=["GET"])
def show_edit_trip(id):
    db=connectToMySQL("handy_helper")
    query="SELECT * FROM jobs WHERE job_id=%(id)s;"
    data={
        'id': session ['id']
    }
    jobs=db.query_db(query,data)
    print(jobs)
    return render_template("edit.html", job=jobs)

@app.route("/destroy/job", methods=["POST"])
def destroy_job():
    db=connectToMySQL("handy_helper")
    query= "DELETE FROM jobs WHERE job_id=%(id)s;"
    data={
        'id': request.form['job_id']
    }
    jobs=db.query_db(query, data)
    return redirect("/dashboard")

@app.route("/destroy")
def clear_session():
    session.pop('id')
    print("logged out")
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)