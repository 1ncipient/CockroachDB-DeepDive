"""
Author: 1ncipient

Edited by: 

The AuthManager class is responsible for handling user registration and login transactions.

The class wraps the database connection, and the class methods wrap transactions for user registration and login.

The class also provides utility functions to hash and verify passwords using the bcrypt algorithm.

"""
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy_cockroachdb import run_transaction
from movieRatingSystem.model.models import User
import os
from typing import List
import movieRatingSystem.transactions as transactions

AUTH_URL = os.getenv("AUTH_URL")

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
        self.Session = scoped_session(sessionmaker(bind=self.engine))

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
    
    @staticmethod
    def validate_length(text: str, text_type: str):
        """
        Validates the length of the username and password.
        """
        if text_type == "username" and (len(text) > USERNAME_MAX_LENGTH or len(text) < USERNAME_MIN_LENGTH):
            raise ValueError("Username does not meet length requirements (3-16 characters).")
        if text_type == "password" and (len(text) > PASSWORD_MAX_LENGTH or len(text) < PASSWORD_MIN_LENGTH):
            raise ValueError("Password does not meet length requirements (8-24 characters).")
        
    def add_user(self, username: str, email: str, password: str) -> str:
        """
        Wraps a `run_transaction` call that adds a new user to the database.
        """
        AuthManager.validate_length(username, "username")
        AuthManager.validate_length(password, "password")
        hashed_password = self.hash_password(password)
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: transactions.add_user_transaction(session, username, email, hashed_password))
        
    def login_user(self, username: str, password: str) -> User:
        """
        Wraps a `run_transaction` call that logs in a user.
        """
        session = self.Session()
        try:
            user = self._get_user_with_session(session, username, password)
        finally:
            self.Session.remove() # Close the session after the transaction
        return user
        
    def _get_user_with_session(self, session, username: str, password: str) -> User:
        """
        Fetch the user, ensure the user is bound to the session and return it.
        """
        user = transactions.login_user_transaction(session, username, password, self.verify_password)
        if user:
            session.add(user)  # Ensure the user is bound to the session
        return user
        
    def change_password(self, user_id: str, new_password: str) -> None:
        """
        Wraps a `run_transaction` call that changes the password of a user.
        """
        hashed_password = self.hash_password(new_password)
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: transactions.update_password_transaction(session, user_id, hashed_password))
        
    def remove_user(self, user_id: str) -> None:
        """
        Wraps a `run_transaction` call that deletes a user from the database.
        """
        return run_transaction(
            sessionmaker(bind=self.engine),
            lambda session: transactions.delete_user_transaction(session, user_id))
        
    def show_tables(self) -> List:
        """
        Returns a list of tables in the database.
        """
        return self.engine.table_names()
    