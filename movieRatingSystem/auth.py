from flask import Flask, render_template, request, redirect, url_for, flash
import os
from util.connect_with_sqlalchemy import (build_sqla_connection_string,
                                          test_connection)
from AuthManager import AuthManager
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret! (This is to sign session cookies)
# for development environment, this is fine to always create a new secret key, but we should not use a random key for production.
app.secret_key = os.urandom(24)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set. Please set your CockroachDB connection string!")

CONNECTION_STRING = build_sqla_connection_string(DATABASE_URL)

auth_manager = AuthManager(CONNECTION_STRING)

print("Testing connection to the database...")

# Routes
@app.route("/")
def home():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            auth_manager.add_user(username, email, password)
            flash("User registered successfully!", "success")
        except IntegrityError:
            flash("Username or email already exists.", "danger")
        except ValueError as e:
            flash(str(e), "danger")

        # Regardless of success or failure, redirect back to home
        return redirect(url_for("home"))

    # Render the register page on GET request
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = auth_manager.login_user(username, password)
            flash(f"Welcome, {user.username}!", "success")
        except ValueError as e:
            flash(str(e), "danger")

        # Regardless of success or failure, redirect back to home
        return redirect(url_for("home"))

    # Render the login page on GET request
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
