from flask import Flask,render_template
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId
import random
from datetime import date

app  = Flask(__name__)
app.config['MONGO_URI'] = config('MONGO_URI') 
mongo = PyMongo(app)
db_admin = mongo.db.admin_login
db_student = mongo.db.student_login
db_events = mongo.db.b_events
db_venues = mongo.db.venues
db_venue_avail = mongo.db.venue_avail

def get_venue_id():

    last_venue_id      = db_venues.find().sort([('venue_id', -1)]).limit(1)

    try:
        last_venue_id = last_venue_id[0]['venue_id']
    except:
        
        last_venue_id = 0

    return last_venue_id + 1

def generate_random():

    rand = random.randint(1000,9999)
    return rand

def check_random():

    rand = generate_random()

    try:
        db_admin.find_one({ "emp_id": rand })
        check_random()

    except:

        return rand

def insert_admin_login_details():

    
    rand = check_random()
        
    data = {
        "admin_login_id" : 2,
        "emp_id"         : rand,
        "email_id"       : None,
        "user_name"        : None

    }
    db_admin.insert_one(data)

    return "Success"

def insert_student_login_details():

    
    rand = check_random()
        
    data = {
        "student_login_id" : 1,
        "roll_number"      : rand,
        "email_id"         : None,
        "user_name"        : None
    }

    db_student.insert_one(data)

    return "Success"


'''
Events :
	Date 		    : Calender 
	Time 			: Time 
	Event Name 	    : Char 
	Event Venue     : Char 
	Co-ordinators   : Char  
	Form 		    : link 
	Contact Details : link  
	Dept 			: Char 
	Year 			: Char
'''
def insert_events_students():
   
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    data = {

        "event_id"          : 2,
        "date"              : d1,
        "event_name"        : "W3H Club Trivia Time",
        "event_venue"       : "Placement Block - Laurel",
        "co-ordinators"     : "Divya, Hari Prasad, Varsha",
        "form_link"         : "https://forms.gle/9E4ofu5rqPe77cus6",
        "contact_details"   : "9791108129",
        "department"        : "CSE",
        "year_of_study"     : "III",
        "mode"              : "offline",
        "starting_time"     : 3,
        "ending_time"       : 4,
       
    }

    db_events.insert_one(data) 

def insert_venue():

    data = {
        "venue_id"   : 5,
        "venue_name" : "Auditorium"
    }

    db_venues.insert_one(data)

    # print("Success")

def venue_avail():

    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    data = {
        "v_a_id"        : 1,
        "venue_id"      : 1,
        "event_date"    : d1,
        "event_id"      : 1,
        "starting_time" : 3,
        "ending_time"   : 4
       
    }

def get_admin_details(emp_id):

    # print(emp_id)

    # print(type(emp_id))

    admin_details = db_admin.find_one({"emp_id" : int(emp_id)})

    result = False

    if(int(emp_id) == int(admin_details["emp_id"])):

        result = True

        # print(admin_details)

    return result

def get_student_details(roll_number):

    admin_details = db_admin.find_one({"roll_number" : int(roll_number)})

    result = False

    if(int(roll_number) == int(admin_details["roll_number"])):

        result = True

    return result

def add_admin_email(emp_id, load):

    # print(load["identifier"])

    response = db_admin.update({'emp_id': int(emp_id)},  {'$set': {"email_id": load["identifier"]}}) 

    # print(response)

    pass

def add_student_email(roll_number, load):

    # print(load["identifier"])

    response = db_student.update({'roll_number': int(roll_number)},  {'$set': {"email_id": load["identifier"]}}) 

    # print(response)

    pass



@app.route("/", methods=["GET","POST"])
def startpy():

    return "hello" 


if __name__ == "__main__":

    # print(app.config['MONGO_URI'])
    # app.run( debug = True,host="0.0.0.0",port = PORT)
    # insert_login_details()

    # insert_events_students()
    # insert_venue()
    # venue_avail()

    # print(get_venue_id())

    insert_student_login_details()
    