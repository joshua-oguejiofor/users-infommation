from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None
    profile_picture: Optional[str]= None    # base64 string
    profile_picture_mime: Optional[str]= None # MIME type


class UserResponse(UserCreate):
    id: int
    profile_picture: Optional[str]       # base64 string
    profile_picture_mime: Optional[str]  # MIME type
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

