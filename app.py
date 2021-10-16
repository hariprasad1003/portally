from flask import Flask,render_template
import pymongo
from bson.json_util import dumps
from flask_pymongo import PyMongo
import os
from decouple import config
from bson import ObjectId



app  = Flask(__name__)
PORT = 3009

app.config['MONGO_URI'] = config('MONGO_URI') 
mongo = PyMongo(app)
dbenter = mongo.db.data_collection
    
@app.route("/", methods=["GET","POST"])
def startpy():

    result = {

        "Greetings" : "Hello"
    }

    return render_template("index.html")


@app.route("/login", methods=["GET","POST"])
def login():

    result = {

        "Greetings" : "Hello"
    }

    return render_template("login.html")

if __name__ == "__main__":
    print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)