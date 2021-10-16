from flask import Flask, render_template, request, redirect, url_for
from sawo import createTemplate, getContext, verifyToken
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId
import json
import db

app  = Flask(__name__)
PORT = 3009

createTemplate("./templates/partials", flask=True)

API_KEY = config('API_KEY')
app.config['MONGO_URI'] = config('MONGO_URI') 
mongo = PyMongo(app)
db_admin = mongo.db.admin_login
db_events = mongo.db.b_events
db_venues = mongo.db.venues
db_venue_avail = mongo.db.venue_avail

load = ''
loaded = 0

def setPayload(payload):
    global load
    load = payload

def setLoaded(reset=False):
    global loaded
    if reset:
        loaded = 0
    else:
        loaded += 1
        

@app.route("/", methods=["GET"])
def get_home():

    return render_template("home.html")

@app.route("/login/admin", methods=["GET"])
def get_login_admin():

    return render_template("login_admin.html")

@app.route("/login/student", methods=["GET"])
def get_login_student():

    return render_template("login_student.html")

@app.route("/login/admin", methods=["POST"])
def post_login_admin():

    emp_id = request.form['emp_id']
    user_name = request.form['user_name']

    # print(emp_id)

    return redirect(url_for('get_login_admin_sawo', emp_id=emp_id, user_name=user_name))

@app.route("/login/student", methods=["POST"])
def post_login_student():

    roll_number = request.form['roll_number']
    user_name = request.form['user_name']

    # print(roll_number)

    return redirect(url_for('get_login_student_sawo', roll_number=roll_number, user_name=user_name))

@app.route("/login/admin/sawo", methods=["GET"])
def get_login_admin_sawo():

    emp_id = request.args['emp_id']
    user_name = request.args['user_name']
    # print(emp_id, user_name)

    result, email_id, username = db.get_admin_details(emp_id)
    # print(result, email_id, username)

    setLoaded()
    setPayload(load if loaded < 2 else '')
    sawo = {
        "auth_key": API_KEY,
        "to": "login",
        "identifier": "email"
    }

    # print(load)

    if(load and result):

        # print(load)

        if(email_id is None and username is None):

            db.add_admin_email(emp_id, load, user_name)  

            return redirect(url_for('get_dashboard'))

        else:

            return redirect(url_for('get_dashboard'))

    else :

        return render_template("sawo_login.html", sawo=sawo, load=load)

@app.route("/login/student/sawo", methods=["GET"])
def get_login_student_sawo():

    roll_number = request.args['roll_number']
    user_name = request.args['user_name']
    # print(roll_number, user_name)

    result, email_id, username = db.get_student_details(roll_number)
    # print(result, email_id, username)

    setLoaded()
    setPayload(load if loaded < 2 else '')
    sawo = {
        "auth_key": API_KEY,
        "to": "login",
        "identifier": "email"
    }

    if(load and result):

        if(email_id is None and username is None):

            db.add_student_email(roll_number,load, user_name)        

            return redirect(url_for('get_dashboard'))

        else:

            return redirect(url_for('get_dashboard'))

    else :

        return render_template("sawo_login.html", sawo=sawo, load=load)

@app.route("/login", methods=["POST"])
def login_sawo():

    payload = json.loads(request.data)["payload"]
    setLoaded(True)
    setPayload(payload)
    status = 200 if(verifyToken(payload)) else 404

    # print(status)

    return {"status": status}

# @app.route("/", methods=["GET"])
# def get_dashboard():
    # return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
def get_dashboard():

    data = db_events.find().sort("event_date", -1)
    # print(dumps(data))

    return render_template("index.html", result = data)


if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)