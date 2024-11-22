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

from models import User
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
    new_user = User(id=str(user_id),
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    created_at=current_time,
                    last_active=current_time)
    
    session.add(new_user)
    
    return str(user_id)
    
    