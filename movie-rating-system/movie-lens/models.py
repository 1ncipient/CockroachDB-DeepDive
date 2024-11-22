from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy.sql.expression import func

Base = declarative_base()

class User(Base):
    """
    DeclarativeMeta class for the vehicles table.
    
    Args:
        Base (DeclarativeMeta): Base class for model to inherit from.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(24), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_active = Column(DateTime, nullable=True, server_default=func.now(), onupdate=func.now())

    def __init__(self, username, email, hashed_password):
        self.validate_username(username)
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, last_active={self.last_active})>"

    # Utility method to update last active time, but without committing
    def update_last_active(self):
        self.last_active = func.now()

    @staticmethod
    def validate_username(username: str):
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")