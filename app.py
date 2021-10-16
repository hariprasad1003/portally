from flask import Flask, render_template, request, redirect, url_for
from sawo import createTemplate, getContext, verifyToken
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId
import json

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

    return render_template("login.html")

@app.route("/", methods=["POST"])
def post_home():

    roll_number = request.form['roll_number']

    print(roll_number)

    return redirect(url_for('get_login', roll_number=roll_number))

@app.route("/login", methods=["GET"])
def get_login():

    roll_number = request.args['roll_number']

    # print(roll_number, API_KEY)

    setLoaded()
    setPayload(load if loaded < 2 else '')
    sawo = {
        "auth_key": API_KEY,
        "to": "login",
        "identifier": "email"
    }

    if(load):

        return redirect(url_for('get_dashboard'))

    else :

        return render_template("sawo_login.html", sawo=sawo, load=load)

@app.route("/login", methods=["POST"])
def post_login():
    payload = json.loads(request.data)["payload"]
    setLoaded(True)
    setPayload(payload)
    status = 200 if(verifyToken(payload)) else 404

    # print(status)

    return {"status": status}

def get_last_event_id():

    last_venue_id      = db_venues.find().sort([('event_id', -1)]).limit(1)

    try:
        last_venue_id = last_venue_id[0]['event_id']
    except:
        
        last_venue_id = 0

    return last_venue_id + 1

@app.route("/event", methods=["GET"])
def get_event_page():

    data = db_venues.find()

    return render_template("add_event.html", result = data)

@app.route("/event", methods=["POST"])
def post_event_page():

    event_id =  get_last_event_id()   
    data = {

        "event_id"          : int(event_id),
        "date"              : request.form['date'],
        "event_name"        : request.form['event_name'],
        "event_venue"       : request.form['roll_number'],
        "co-ordinators"     : request.form['co-ordinators'],
        "form_link"         : request.form['form_link'],
        "contact_details"   : request.form['contact_details'],
        "department"        : request.form['department'],
        "year_of_study"     : request.form['year_of_study'],
        "mode"              : request.form['mode'],
        "starting_time"     : request.form['roll_number'],
        "ending_time"       : request.form['roll_number'],
       
    }

    # request.form['roll_number']


    return render_template("faq.html")

@app.route("/dashboard", methods=["GET"])
def get_dashboard():

    data = db_events.find().sort("event_date", -1)
    # print(dumps(data))

    return render_template("index.html", result = data)


if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)