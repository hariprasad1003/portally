from flask import Flask,render_template

app  = Flask(__name__)
PORT = 3009

    
@app.route("/", methods=["GET","POST"])
def startpy():

    result = {

        "Greetings" : "Hello"
    }

    return render_template("index.html")


if __name__ == "__main__":
    app.run( debug = True,host="0.0.0.0",port = PORT)