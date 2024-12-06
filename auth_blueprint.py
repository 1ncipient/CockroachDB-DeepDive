from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from movieRatingSystem.util.connect_with_sqlalchemy import (build_sqla_connection_string,
                                          test_connection)
from movieRatingSystem.AuthManager import AuthManager
from sqlalchemy.exc import IntegrityError

# Define the blueprint
auth = Blueprint(
    'auth',
    __name__,
    template_folder='movieRatingSystem/templates'
)

AUTH_URL = os.getenv("AUTH_URL")

if AUTH_URL is None:
    raise ValueError("AUTH_URL environment variable is not set. Please set your CockroachDB connection string!")

CONNECTION_STRING = build_sqla_connection_string(AUTH_URL)

auth_manager = AuthManager(CONNECTION_STRING)

# Routes
@auth.route("/")
def home():
    return render_template("base.html")

@auth.route("/register", methods=["GET", "POST"])
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

        return redirect(url_for("auth.home"))

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    print("\n=== Login Route ===")
    print(f"Method: {request.method}")
    print(f"Session before login: {session}")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = auth_manager.login_user(username, password)
            if user:
                session.permanent = False
                session['user_id'] = user.id
                print(f"Login successful. Session after login: {session}")
                next_url = session.pop('next', '/movies/search')
                print(f"Redirecting to: {next_url}")
                return redirect(next_url)
            else:
                print("Login failed: Invalid credentials")
                flash("Invalid username or password.", "danger")
        except ValueError as e:
            flash(str(e), "danger")

        return redirect(url_for("auth.home"))

    return render_template("base.html")

@auth.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.home"))