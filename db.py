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
db_events = mongo.db.b_events


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

def insert_login_details():

    
    rand = check_random()
        
    data = {
        "admin_login_id" : 2,
        "emp_id"         : rand,
        "email_id"       : None,
        "user_id"        : None

    }
    db_admin.insert_one(data)

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
        "event_id"          : 1,
        "date"              : d1,
        "event_name"        : "W3H Club coding event",
        "event_venue"       : "Placement block Basil",
        "co-ordinators"     : "Divya, Hari Prasad, Varsha",
        "form_link"         : "https://forms.gle/9E4ofu5rqPe77cus6",
        "contact_details"   : "9791108129",
        "department"        : "CSE",
        "year_of_study"     : "III"
    }

    db_events.insert_one(data)

@app.route("/", methods=["GET","POST"])
def startpy():

    return "hello" 


if __name__ == "__main__":

    # print(app.config['MONGO_URI'])
    # app.run( debug = True,host="0.0.0.0",port = PORT)
    # insert_login_details()

    insert_events_students()