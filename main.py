from flask import Blueprint, render_template, redirect

main = Blueprint("main", __name__)

@main.route("/")
def index():
    # Redirect the root URL to /home
    return redirect("/home")