"""
Author: 1ncipient

Edited by: 

Defines the transactions that are performed by the AuthManager class.

Where python code meets the database, transactions are used to group multiple operations into a single unit of work.

This ensures that the database remains in a consistent state, and that the operations are either all completed successfully, or none of them are.

ACID properties of transactions:
- Atomicity: All operations in a transaction are completed successfully, or none of them are.
- Consistency: The database remains in a consistent state before and after the transaction.
- Isolation: Transactions are isolated from each other, and do not interfere with each other.
- Durability: Changes made by a transaction are permanent and are not lost.
"""

from movieRatingSystem.models.auth_models import User
from uuid import uuid4
from sqlalchemy.sql.expression import func

def add_user_transaction(session, username, email, hashed_password) -> str:
    """
    Insert a new user into the users table.
    
    Args:
        session: {.Session} -- The active session for the database connection.
        username: {str} -- The username of the new user.
        email: {str} -- The email of the new user.
        hashed_password: {str} -- The hashed password of the new user.
    
    Returns:
        user_id {UUID} -- The UUID of the new user.
    """
    # Generate new uuid
    user_id = uuid4()
    # Current time on database server
    current_time = func.now()
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    new_user.created_at = current_time
    new_user.last_active = current_time
    
    session.add(new_user)
    
    return str(user_id)
    
def login_user_transaction(session, username: str, plain_password: str, verify_password) -> User:
    """
    Verifies the user credentials and retrieves user object.
    
    Args:
        session: {.Session} -- The active session for the database connection.
        username: {str} -- The username of the user.
        plain_password: {str} -- The password of the user.
    
    Returns:
        {User} -- The user object if the credentials are valid.
    """
    user = session.query(User).filter(User.username == username).first()
    
    if not user:
        raise ValueError("User does not exist.")
    
    if not verify_password(plain_password, user.hashed_password):
        raise ValueError("Invalid credentials.")
    
    user.update_last_active()

    # Make sure the user object is still attached to the session
    session.add(user)  # Attach the user object to the session explicitly
    
    return user


def update_password_transaction(session, user_id: str, hashed_password: str) -> bool:
    """
    Update the password of a user.
    
    Args:
        session: {.Session} -- The active session for the database connection.
        user_id: {str} -- The UUID of the user.
        hashed_password: {str} -- The new hashed password.
    """
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    user.hashed_password = hashed_password
    user.update_last_active()
    return True
    
def remove_user_transaction(session, user_id: str) -> bool:
    """
    Remove a user from the users table.
    
    Args:
        session: {.Session} -- The active session for the database connection.
        user_id: {str} -- The UUID of the user to be removed.
    """
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    session.delete(user)
    return True