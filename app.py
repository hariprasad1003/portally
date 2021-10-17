from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask.app import setupmethod
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
from flask_googlemaps import GoogleMaps, icons
from flask_googlemaps import Map
from werkzeug.utils import secure_filename

app  = Flask(__name__)
PORT = 3009

app.config["UPLOAD_FOLDER"] = "static"

createTemplate("./templates/partials", flask=True)

SAWO_API_KEY = config('SAWO_API_KEY')
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
app.config['MONGO_URI'] = config('MONGO_URI') 
mongo = PyMongo(app)
db_admin = mongo.db.admin_login
db_b_events = mongo.db.b_events
db_a_events = mongo.db.a_events
db_venues = mongo.db.venues
db_venue_avail = mongo.db.venue_avail
db_notes = mongo.db.notes

GoogleMaps(app, key=GOOGLE_API_KEY)

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
    user_name   = request.form['user_name']

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
        "auth_key": SAWO_API_KEY,
        "to": "login",
        "identifier": "email"
    }

    # print(load)

    if(load and result):

        # print(load)

        if(email_id is None and username is None):

            db.add_admin_email(emp_id, load, user_name)  

            return redirect(url_for('get_dashboard_admin'))

        else:

            return redirect(url_for('get_dashboard_admin'))

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
        "auth_key": SAWO_API_KEY,
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

    last_event_id      = db_b_events.find().sort([('event_id', -1)]).limit(1)

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
        "event_date"    : form_date,
        "event_id"      : int(event_id),
        "starting_time" : float(request.form['starting_time']),
        "ending_time"   : float(request.form['ending_time'])
    }


    for data in db_venue_avail.find({"venue_id":venue_id["venue_id"]}):

        print("form date", form_date)
        event_data = data["event_date"]
        print("event date", event_data)
        # form_date = string_date(request.form['date'])

        if( event_data == form_date):

            print("Inside for loop", data)
            db_start = float(data["starting_time"])
            db_end   = float(data["ending_time"])

            form_start = float(request.form['starting_time'])
            form_end   = float(request.form['ending_time']) 


            print(db_start,db_end, form_start, form_end )

            if((db_start >= form_start or db_end >= form_start) and (db_start >= form_end or db_end <= form_end)  ):
                message = "Venue is already booked in the given time"
                print("message", message)
                flag=1
       
    if(flag==0):
        db_b_events.insert_one(data)
        db_venue_avail.insert_one(venue_data)
        message = "Successfully sent for approval"


    return render_template("success.html", message = message)

def string_date(str_date):

    dt_string = str_date


    dt_object1 = datetime.strptime(dt_string, "%Y-%m-%d")
    print("dt_object1 =", dt_object1)

    return dt_object1
  
@app.route("/dashboard-admin", methods=["GET"])
def get_dashboard_admin():

    data = db_a_events.find().sort("event_date", -1)


    data_1 = db_b_events.find().sort("event_date", -1)


    return render_template("admin_index.html", result = data, result_1 = data_1)


@app.route("/approve/<event_id>", methods=["GET"])
def get_dashboard_admin_approve(event_id):

    print(event_id)

    data = db_b_events.find_one({"event_id":int(event_id)})

    print (data)

    db_a_events.insert_one(data)
    # db_b_events.delete_one({"event_id":int(event_id)})


    return redirect(url_for('get_dashboard_admin'))

@app.route("/dashboard", methods=["GET"])
def get_dashboard():

    data = db_a_events.find().sort("event_date", -1)
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

    data_list = []

    for itr in data:

        value = {}

        value = itr 

        data_1 = db_b_events.find_one({"event_id": itr["event_id"]}) 

        value["event_name"] = data_1["event_name"]

        data_list.append(value)

    print(data_list)   

    return render_template("single_venue_details.html", result=data_list)



@app.route("/map", methods=["GET"])
def get_map():

    '''
    MGR Statue - 12.869569320901709, 80.21578432923627

    Admin Block - 12.869261957286394, 80.21695868772133
    Library - 12.869752082420984, 80.2148993654051
    Book Bank - 12.868917935184149, 80.21485294143628
    EEE Dept 1 - 12.86913506393891, 80.21516822487982
    EEE Dept 2 - 12.868991251408364, 80.2154516907258
    Civil Dept - 12.869010990388016, 80.21577275918398
    CSE Dept - 12.87006279377722, 80.21685744992764
    CSE Laboratory - 12.87009663188254, 80.21668100690107
    EEE Laboratory - 12.870260182673032, 80.21646406876486
    Mechanical Laboratory - 12.870248903312467, 80.2160099449096
    EIE Dept - 12.870446292045141, 80.2152202900461
    Exam Block - 12.87078467238549, 80.21634547591113
    Placement Block - 12.870959502043675, 80.21724215359554

    '''

    # sndmap=Map(
    #     zoom=18,
    #     maptype="ROADMAP",
    #     identifier ="sndmap",
    #     lat=12.870002002625137,
    #     lng=80.21836282448177,
    #     markers=[
    #         {
    #             'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
    #             'lat':12.869892286997779,
    #             'lng':80.2184995084505,
    #             'infobox':(
    #                 "<h2>St.Joseph's College Of Engineering<h2>"
    #                 "<img src='./static/images/stjoseph.png'>"
    #                 )
    #         }
    #     ],
    #     language="en",
    #     region="IN",
    #     style="height:700px;width:1000px;margin:20;"
    # )
    
    sndmap=Map(
        zoom=18,
        maptype="ROADMAP",
        identifier ="sndmap",
        lat=12.869569320901709,
        lng=80.21578432923627,
        markers=[
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.869261957286394,
                'lng':80.21695868772133,
                'infobox':(
                    "<p>Admin Block<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.869752082420984,
                'lng':80.2148993654051,
                'infobox':(
                    "<p>Library<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.868917935184149,
                'lng':80.21485294143628,
                'infobox':(
                    "<p>Book Bank<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.86913506393891,
                'lng':80.21516822487982,
                'infobox':(
                    "<p>EEE Dept 1<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.868991251408364,
                'lng':80.2154516907258,
                'infobox':(
                    "<p>EEE Dept 2 <p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.869010990388016,
                'lng':80.21577275918398,
                'infobox':(
                    "<p>Civil Dept<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.87006279377722,
                'lng':80.21685744992764,
                'infobox':(
                    "<p>CSE Dept<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.87009663188254,
                'lng':80.21668100690107,
                'infobox':(
                    "<p>CSE Laboratory<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.870260182673032,
                'lng':80.21646406876486,
                'infobox':(
                    "<p>EEE Laboratory<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.870248903312467,
                'lng':80.2160099449096,
                'infobox':(
                    "<p>Mechanical Laboratory<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.870446292045141,
                'lng':80.2152202900461,
                'infobox':(
                    "<p>EIE Dept<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.87078467238549,
                'lng':80.21634547591113,
                'infobox':(
                    "<p>Exam Block<p>"
                    )
            },
            {
                'icon':'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':12.870959502043675,
                'lng':80.21724215359554,
                'infobox':(
                    "<p>Placement Block<p>"
                    )
            },
        ],
        language="en",
        region="IN",
        style="height:700px;width:1000px;margin:20;"
    )

    return render_template('map.html', 
        sndmap=sndmap
        )

@app.route("/notes", methods=["GET"])
def get_notes():

    result = db.get_notes()

    # print(result)

    return render_template('notes.html', result=result)

@app.route("/notes", methods=["POST"])
def post_notes():

    year_of_study   = request.form['year_of_study']
    semester        = request.form['semester']
    subject         = request.form['subject']
    dept            = request.form['dept']

    data = {

        'year_of_study' : year_of_study,
        'semester'      : int(semester),
        'subject'       : subject,
        'dept'          : dept

    }

    print(data)

    result = db_notes.find(data)

    # print(result)

    notes_obj = []

    for notes in result:

        # print(notes)

        notes_obj.append(notes)

    print(notes_obj)

    # return "hello"

    return render_template('notes.html', result=notes_obj)

@app.route("/notes/download/<notes_name>", methods=["GET"])
def get_download_notes(notes_name):

    filename = notes_name + '.pdf'

    path = app.config['UPLOAD_FOLDER'] + '/' + 'notes' + '/' + filename

    return send_file(path, as_attachment=True, attachment_filename=filename)

@app.route("/notes/admin", methods=["GET"])
def get_admin_notes():

    result = db.get_notes()

    return render_template('admin_notes.html', result = result)

@app.route("/notes/admin", methods=["POST"])
def post_admin_notes():

    if request.method == 'POST':

        year_of_study   = request.form['year_of_study']
        dept            = request.form['dept']
        semester        = request.form['semester']
        subject         = request.form['subject']

        result = db_notes.find({'subject': subject})

        for notes_details in result:

            subject_code = notes_details['notes_name']

        notes = request.files['notes']

        notes_filename = secure_filename(notes.filename)

        # print(notes_filename)

        extension = notes_filename.split('.')[1]

        path = app.config['UPLOAD_FOLDER'] + '/' + 'notes' + '/' + subject_code + '.' + extension

        # print(path)

        notes.save(path)

        # # print(year_of_study, semester, subject_name, subject_code)

        message = 'Notes Uploaded Successfully'

        return render_template("success.html", message = message)

if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)