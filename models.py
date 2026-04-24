from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    bio = Column(Text, nullable=True)

    # Profile picture stored as base64-encoded string
    profile_picture = Column(Text, nullable=True)
    profile_picture_mime = Column(String(50), nullable=True)  # e.g. "image/jpeg"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
