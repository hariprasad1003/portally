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
dbenter = mongo.db.data_collection

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

        return render_template("sawo_login.html")

@app.route("/login", methods=["POST"])
def post_login():
    payload = json.loads(request.data)["payload"]
    setLoaded(True)
    setPayload(payload)
    status = 200 if(verifyToken(payload)) else 404

    # print(status)

    return {"status": status}

@app.route("/dashboard", methods=["GET"])
def get_dashboard():

    return render_template("index.html")


if __name__ == "__main__":
    # print(app.config['MONGO_URI'])
    app.run( debug = True,host="0.0.0.0",port = PORT)