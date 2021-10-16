from flask import Flask, render_template, request, redirect, url_for
from sawo import createTemplate, getContext, verifyToken
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId
import json
from datetime import datetime
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

def get_last_event_id():

    last_event_id      = db_events.find().sort([('event_id', -1)]).limit(1)

    try:
        last_event_id = last_event_id[0]['event_id']
    except:
        
        last_event_id = 0

    return last_event_id + 1

@app.route("/event", methods=["GET"])
def get_event_page():

    data = db_venues.find()

    return render_template("add_event.html", result = data)


def get_venue_avail_id():

    last_venue_avail_id      = db_venue_avail.find().sort([('v_a_id', -1)]).limit(1)

    try:
        last_venue_avail_id = last_venue_avail_id[0]['v_a_id']
    except:
        
        last_venue_avail_id = 0

    return last_venue_avail_id + 1

@app.route("/event", methods=["POST"])
def post_event_page():

    event_id =  get_last_event_id()
    flag = 0
    form_date = string_date(request.form['date'])
    data = {

        "event_id"          : int(event_id),
        "date"              : form_date,
        "event_name"        : request.form['event_name'],
        "event_venue"       : request.form['event_venue'],
        "co-ordinators"     : request.form['co-ordinators'],
        "form_link"         : request.form['form_link'],
        "contact_details"   : request.form['contact_details'],
        "department"        : request.form['department'],
        "year_of_study"     : request.form['year_of_study'],
        "mode"              : request.form['mode'],
        "starting_time"     : request.form['starting_time'],
        "ending_time"       : request.form['ending_time'],
    }

    print(data)
    
    v_a_id = get_venue_avail_id()

    venue_id = db_venues.find_one({"venue_name" : request.form['event_venue']})

    print(venue_id["venue_id"])

    venue_data = {
        "v_a_id"        : v_a_id,
        "venue_id"      : venue_id["venue_id"],
        "event_date"    : request.form['date'],
        "event_id"      : int(event_id),
        "starting_time" : float(request.form['starting_time']),
        "ending_time"   : float(request.form['ending_time'])
    }


    for data in db_venue_avail.find({"venue_id":venue_id["venue_id"]}):

        event_data = data["event_date"]
        # form_date = string_date(request.form['date'])

        if( event_data == form_date):

            print("Inside for loop", data)
            db_start = float(data["starting_time"])
            db_end   = float(data["ending_time"])

            form_start = float(request.form['starting_time'])
            form_end   = float(request.form['ending_time']) 


            print(db_start,db_end, form_start, form_end )

            if(db_start >= form_start and db_end <= form_end ):
                message = "Venue is already booked in the given time"
                flag=1
       
    if(flag==0):
        db_events.insert_one(data)
        db_venue_avail.insert_one(venue_data)
        message = "Successfully sent for approval"


    return render_template("success.html", message = message)

def string_date(str_date):

    dt_string = str_date


    dt_object1 = datetime.strptime(dt_string, "%Y-%m-%d")
    print("dt_object1 =", dt_object1)

    return dt_object1
  
# @app.route("/", methods=["GET"])
# def get_dashboard():
    # return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
def get_dashboard():

    data = db_events.find().sort("event_date", -1)
    # print(dumps(data))

    return render_template("index.html", result = data)


@app.route("/venues", methods=["GET"])
def get_venues():

    data = db_venues.find()
    # print(dumps(data))

    return render_template("venues_details.html", result=data)


@app.route("/venue/<venue_id>", methods=["GET"])
def get_venue_details(venue_id):

    data = db_venue_avail.find({"venue_id": int(venue_id)})
    # print(dumps(data))



    # for itr in data:
    #     data_1 = db_events.find_one({"event_id":itr["event_id"]}) 
    #     itr["event_name"] = data_1["event_name"]
        # print(itr)

    # print(dumps(data))
    return render_template("single_venue_details.html", result=data)

# /venue/

if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)