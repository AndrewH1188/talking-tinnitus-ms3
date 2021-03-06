# The code that I have used for this has come
# from the Code Institute Task Manager
# Mini project, but has been amended in
# places to fit with my code for the different pages.

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


# Home / Index page
@app.route("/")
@app.route("/home")
def home():
    title = "Talking Tinnitus | Home"
    return render_template("index.html", title=title)


# About Us page
@app.route("/about")
def about():
    title = "Talking Tinnitus | About Us"
    return render_template("about-us.html", title=title)


# Show Entries
@app.route("/get_entry")
def get_entry():
    entry = list(mongo.db.entry.find())
    title = "Talking Tinnitus | Community Entries"
    return render_template("entries.html", entry=entry, title=title)


# Search Entries
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    entry = list(mongo.db.entry.find({"$text": {"$search": query}}))
    return render_template("entries.html", entry=entry)


# Register / Sign Up
@app.route("/register", methods=["GET", "POST"])
def register():
        title = "Talking Tinnitus | Register / Sign up"
        if request.method == "POST":
            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            # check if email already exists in db
            existing_email = mongo.db.users.find_one(
                {"email": request.form.get("email")})

            if existing_user:
                flash("Username already exists")
                return redirect(url_for("register"))

            if existing_email:
                flash("Email already exists")
                return redirect(url_for("register"))

            else:
                register = {
                    "email": request.form.get("email"),
                    "username": request.form.get("username").lower(),
                    "password": generate_password_hash
                    (request.form.get("password"))
                }
            mongo.db.users.insert_one(register)

            # put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
            return redirect(url_for("profile", username=session["user"]))

        return render_template("register.html", title=title)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    title = "Talking Tinnitus | Log in"
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # Code for the rest of the Log in
        # (down to the end of the else statement)
        # by Igor at Tutor Support

        # check if email exists in db
        if existing_user:
            if existing_user["email"] == request.form.get("email").lower():
                # ensure hashed password matches user input
                if check_password_hash(
                     existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        return redirect(url_for(
                                "profile", username=session["user"]))
                else:
                    flash("Incorrect Password")
                    return redirect(url_for("login"))
            else:
                flash("Incorrect Email Address")
                return redirect(url_for("login"))
        else:
            flash("Incorrect Username")
            return redirect(url_for("login"))

    return render_template("login.html", title=title)


# User profile
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    title = "Talking Tinnitus | My Profile"
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username, title=title)

    return redirect(url_for("login"))


# Log out
@app.route("/logout")
def logout():
    title = "Talking Tinnitus | Log in"
    # remove user from session cookie
    session.pop("user")
    return redirect(url_for("login", title=title))


# Add entry
@app.route("/add_entry", methods=["GET", "POST"])
def add_entry():
    title = "Talking Tinnitus | Add Community Entry"
    if request.method == "POST":
        entry = {
            "category_name": request.form.get("category_name"),
            "entry_description": request.form.get("entry_description"),
            "entry_details": request.form.get("entry_details"),
            "created_by": session["user"],
            "created_date": date.today().isoformat()
        }
        mongo.db.entry.insert_one(entry)
        flash("Thank you for submitting your entry")
        return redirect(url_for("get_entry"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add-entry.html",
                           title=title, categories=categories)


# Edit entry
@app.route("/edit_entry/<entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    title = "Talking Tinnitus | Edit Entry"
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "entry_description": request.form.get("entry_description"),
            "entry_details": request.form.get("entry_details"),
            "created_by": session["user"],
            "created_date": date.today().isoformat()
        }
        mongo.db.entry.update({"_id": ObjectId(entry_id)}, submit)
        return redirect(url_for("get_entry"))

    entry = mongo.db.entry.find_one({"_id": ObjectId(entry_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit-entry.html", entry=entry,
                           categories=categories, title=title)


# delete entry
@app.route("/delete_entry/<entry_id>")
def delete_entry(entry_id):
    mongo.db.entry.remove({"_id": ObjectId(entry_id)})
    flash("Entry Successfully Deleted")
    return redirect(url_for("get_entry"))


# Find category
@app.route("/get_categories")
def get_categories():
    title = "Talking Tinnitus | Manage Categories"
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("manage-categories.html",
                           categories=categories, title=title)


# Add category
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    title = "Talking Tinnitus | Add Category"
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        return redirect(url_for("get_categories"))

    return render_template("add-category.html", title=title)


# Edit category
@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    title = "Talking Tinnitus | Edit Category"
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit-category.html",
                           category=category, title=title)


# delete category
@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# Contact Us
@app.route("/contact")
def contact():
    title = "Talking Tinnitus | Contact Us"
    return render_template("contact-us.html", title=title)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
