from flask import Blueprint, render_template, redirect

main = Blueprint("main", __name__)


@main.route("/home")
@main.route("/")
def index():
    return redirect('/movies/search')