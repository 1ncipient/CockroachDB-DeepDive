from flask import Flask
import os
from util.connect_with_sqlalchemy import (build_sqla_connection_string,
                                          test_connection)
from movie-lens.AuthManager import AuthManager

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set. Please set your CockroachDB connection string!")

CONNECTION_STRING = build_sqla_connection_string(DATABASE_URL)

auth_manager = AuthManager(CONNECTION_STRING)

print("Testing connection to the database...")



@app.route('/')
def home():
    return "Welcome to the Flask app!"

@app.route('/register', methods=['POST'])
def register_user():
    pass

if __name__ == "__main__":
    # Run the app
    app.run(debug=True)
