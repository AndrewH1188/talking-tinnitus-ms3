# The code that I have used for this has come from the Code Institute Task Manager 
# Mini project, but has been amended in places to fit with my code for the different pages.

import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_entry")
def get_entry():
    entry = list(mongo.db.entry.find())
    print(entry)
    return render_template("entries.html", entry=entry)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    entry = list(mongo.db.entry.find({"$text": {"$search": query}}))
    return render_template("entries.html", entry=entry)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
