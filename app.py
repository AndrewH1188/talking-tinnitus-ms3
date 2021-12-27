# The code that I have used for this has come from the Code Institute Task Manager 
# Mini project, but has been amended in places to fit with my code for the different pages.

import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    title = "Talking Tinnitus | Home"
    return render_template("index.html", title=title)


@app.route("/about")
def about():
    title = "Talking Tinnitus | About Us"
    return render_template("about-us.html", title=title)


@app.route("/get_entry")
def get_entry():
    entry = list(mongo.db.entry.find())
    print(entry)
    title = "Talking Tinnitus | Community Entries"
    return render_template("entries.html", entry=entry, title=title)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    entry = list(mongo.db.entry.find({"$text": {"$search": query}}))
    return render_template("entries.html", entry=entry)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        # check if email already exists in db
        existing_email = mongo.db.email.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("Username or email address already exists")
            return redirect(url_for("register"))

        register = {
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Email Address and/or Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Email Address and/or Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# add entries
@app.route("/add_entry", methods=["GET", "POST"])
def add_entry():
    title = "Talking Tinnitus | Add Community Entry"
    if request.method == "POST":
        entry = {
            "category_name": request.form.get("category_name"),
            "entry_description": request.form.get("entry_description"),
            "entry_details": request.form.get("entry_details"),
            "created_by": session["user"],
            "created_date": session["date"]
        }
        mongo.db.entry.insert_one(entry)
        flash("Thank you for submitting your entry")
        return redirect(url_for("get_entry"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add-entry.html", title=title, categories=categories)


@app.route("/contact")
def contact():
    title = "Talking Tinnitus | Contact Us"
    return render_template("contact-us.html", title=title)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
