# Group-60
# Di Cao 963908,
# Yannan Gao 1015229
# Boyang Zhang 1069342
# Chenqin Zhang 733301
# Yiran Zhang 966673
from flask import Flask, render_template
import couchdb


app = Flask(__name__)
couch = couchdb.Server("http://admin:admin@172.26.130.241:5984/")
db = couch['result']

# Route - The Main Page
@app.route("/")
@app.route("/index")
def index():

    return render_template("index.html")


# Route - Senerios
@app.route("/scenario1/<number>")
def senario1(number):
    # file_name =
    return render_template("scenario1.html")#, senario_id=number)

@app.route("/scenario2/<number>")
def senario2(number):

    return render_template("scenario2.html")#, senario_id=number)

@app.route("/scenario3/<number>")
def senario3(number):

    return render_template("scenario3.html")#, senario_id=number)


# Route - Database
@app.route("/data/result/<result_id>")
def result(result_id):
    tmp = db[result_id]
    return tmp

@app.route("/data/aurin/<number>")
def aurin(number):
    return


if __name__ == "__main__":
    app.run(debug=True)
