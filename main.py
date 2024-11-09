from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/home")
@main.route("/")
def index():
    return render_template("index.html")
