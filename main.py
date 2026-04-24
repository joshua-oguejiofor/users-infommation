

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import base64
from database import get_db
from database import SessionLocal, engine, Base
from models import Users
from schemas import UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User CRUD with Profile Picture", version="1.0.0")

app.add_middleware( CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB




# ── CREATE ──────────────────────────────────────────────────────────────────
@app.post("/users/", response_model=UserCreate, status_code=201)
async def create_user(name: str = Form(...), email: str = Form(...), bio: Optional[str] = Form(None), profile_picture: Optional[UploadFile] = File(None), db: Session = Depends(get_db),):

    """Create a new user, optionally with a profile picture."""
    # Check email uniqueness
    if db.query(Users).filter(Users.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    image_data = None
    image_mime = None

    if profile_picture:
        if profile_picture.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type '{profile_picture.content_type}'. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )
        raw = await profile_picture.read()
        if len(raw) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image exceeds 5 MB limit")
        image_data = base64.b64encode(raw).decode("utf-8")
        image_mime = profile_picture.content_type

    user = Users(
        name= name,
        email= email,
        bio= bio,
        profile_picture= image_data,
        profile_picture_mime= image_mime,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── READ ALL ─────────────────────────────────────────────────────────────────

@app.get("/users/", response_model= list[UserResponse], status_code= 200)
async def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Return a paginated list of users."""
    user= db.query(Users).offset(skip).limit(limit).all()
    return user



# ── READ ONE ─────────────────────────────────────────────────────────────────

@app.get("/users/{user_id}", response_model= UserResponse, status_code= 200)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Return a single user by ID."""
    user= db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── UPDATE ────────────────────────────────────────────────────────────────────

@app.put("/users/{user_id}", response_model=UserResponse, status_code= 200)
async def update_user(
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):

    """Update user fields. Only provided fields are changed."""
    user= db.get(Users, user_id )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if name:
        user.name = name
    if email:
        conflict = (
            db.query(Users)
            .filter(Users.email == email, Users.id != user_id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = email
    if bio is not None:
        user.bio = bio

    if profile_picture:
        if profile_picture.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type '{profile_picture.content_type}'",
            )
        raw = await profile_picture.read()
        if len(raw) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image exceeds 5 MB limit")
        user.profile_picture = base64.b64encode(raw).decode("utf-8")
        user.profile_picture_mime = profile_picture.content_type

    db.commit()
    db.refresh(user)
    return user


# ── DELETE ────────────────────────────────────────────────────────────────────

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Permanently delete a user."""
    user= db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


# ── PROFILE PICTURE ───────────────────────────────────────────────────────────

@app.delete("/users/{user_id}/picture", response_model= UserResponse, status_code= 200)
async def remove_profile_picture(user_id: int, db: Session = Depends(get_db)):
    """Remove only the profile picture of a user."""
    user= db.get(Users, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.profile_picture = None
    user.profile_picture_mime = None
    db.commit()
    db.refresh(user)
    return user
