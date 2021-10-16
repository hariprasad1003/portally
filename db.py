from flask import Flask,render_template
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId
import random

app  = Flask(__name__)
app.config['MONGO_URI'] = config('MONGO_URI') 
mongo = PyMongo(app)
db_admin = mongo.db.admin_login


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

@app.route("/", methods=["GET","POST"])
def startpy():

    return "hello" 


if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    # app.run( debug = True,host="0.0.0.0",port = PORT)
    insert_login_details()