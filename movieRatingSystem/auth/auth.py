from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import os
import traceback
from ..utils.connect_with_sqlalchemy import build_sqla_connection_string
from .AuthManager import AuthManager
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__, template_folder='../templates', static_folder='../static')

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set!")

CONNECTION_STRING = build_sqla_connection_string(DATABASE_URL)

auth_manager = AuthManager(CONNECTION_STRING)

# Root auth route (login page)
@auth.route("/")
@auth.route("/login")  # Add this line to handle both paths
def login():
    return render_template("base.html")

# Login POST handler
@auth.route("/login", methods=["POST"])
def login_post():
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        current_app.logger.debug(f"Login attempt for {username}")

        try:
            user = auth_manager.login_user(username, password)
            if user:
                session['user_id'] = user.id
                flash(f"Welcome, {user.username}!", "success")
                return redirect('/movies')  # Changed from '/movies/search' to '/movies'
            else:
                flash("Invalid username or password.", "danger")
        except ValueError as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash(str(e), "danger")

        return redirect(url_for("auth.login"))
    except Exception as e:
        current_app.logger.error(f"Unexpected error during login: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise

@auth.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            current_app.logger.debug(f"Registration attempt for {username}")

            try:
                auth_manager.add_user(username, email, password)
                flash("User registered successfully!", "success")
                return redirect(url_for("auth.login"))
            except IntegrityError:
                flash("Username or email already exists.", "danger")
            except ValueError as e:
                flash(str(e), "danger")

        return render_template("register.html")
    except Exception as e:
        current_app.logger.error(f"Exception in register route: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise

@auth.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))