"""
Author: 1ncipient

Edited by: 

The AuthManager class is responsible for handling user registration and login transactions.

The class wraps the database connection, and the class methods wrap transactions for user registration and login.

The class also provides utility functions to hash and verify passwords using the bcrypt algorithm.

"""
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_cockroachdb import run_transaction
from models import User
import os
import typing

DATABASE_URL = os.getenv("DATABASE_URL")

# Username and Password Character Limits
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 24
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 24

class AuthManager:
    """
    Wraps the database connection, and the class methods wrap transactions for user registration and login.
    """
    def __init__(self, conn_string: str):
        self.engine = create_engine(conn_string)
        self.connection_string = conn_string
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Utility function to hash passwords
    def hash_password(self, password: str) -> str:
        """
        Hashes the provided password using the bcrypt algorithm.
        """
        return self.pwd_context.hash(password)

    # Verify the provided password against the stored hash
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies the provided password against the stored hash
        """
        return self.pwd_context.verify(plain_password, hashed_password)

"""
# Register a new user
@auth_blueprint.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Use the database session provided by get_db()
    db: Session = next(get_db())

    # Check if the username or email already exists
    user = db.query(User).filter_by(username=username).first()
    if user:
        return jsonify({"message": "Username already registered"}), 400

    # Create a new user
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    
    # Add the new user to the session and commit
    db.add(new_user)
    db.commit()

    return jsonify({"message": "User registered successfully", "user": username}), 201

# Login a user
@auth_blueprint.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Use the database session provided by get_db()
    db: Session = next(get_db())

    # Look up the user by username
    user = db.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Update last active time (without committing in the model)
    user.update_last_active()

    # Commit the session after updating the last_active field
    db.commit()

    return jsonify({"message": "Login successful", "last_active": user.last_active}), 200
"""