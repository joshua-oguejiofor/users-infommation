```bash

# FastAPI User CRUD with Profile Picture Upload

A complete REST API built with **FastAPI** and **SQLite** that supports full CRUD operations for users, including profile picture upload stored directly in the database as Base64.

---

## Features

| Feature | Detail |
|---|---|
| Create user | `POST /users/` with optional profile picture |
| List users | `GET /users/?skip=0&limit=20` |
| Get user | `GET /users/{id}` |
| Update user | `PUT /users/{id}` — partial updates supported |
| Delete user | `DELETE /users/{id}` |
| Remove picture | `DELETE /users/{id}/picture` |

- Accepted image types: **JPEG, PNG, GIF, WebP**
- Max image size: **5 MB**
- Images stored as **Base64** strings in SQLite
- Auto-generated **Swagger UI** at `/docs`

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload
``

The API will be available at **http://127.0.0.1:8000**
Interactive docs at **http://127.0.0.1:8000/docs**

---

## API Usage Examples

### Create a user (with picture)
```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -F "name=Oguejiofor Joshua" \
  -F "email= josh@example.com" \
  -F "bio=Software engineer" \
  -F "profile_picture=@/path/to/photo.jpg"
```

### Create a user (without picture)
```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -F "name=Bob Jones" \
  -F "email=bob@example.com"
```

### List users
```bash
curl http://127.0.0.1:8000/users/
```

### Get a user
```bash
curl http://127.0.0.1:8000/users/1
```

### Update user (change name and picture)
```bash
curl -X PUT http://127.0.0.1:8000/users/1 \
  -F "name=Alice Johnson" \
  -F "profile_picture=@/path/to/new_photo.png"
```

### Delete a user
```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```

### Remove only the profile picture
```bash
curl -X DELETE http://127.0.0.1:8000/users/1/picture


---

## Response Schema

 ```json
{
  "id": 1,
  "name": "oguejiofor joshua",
  "email": "josh@example.com",
  "bio": "Software engineer",
  "profile_picture": "<base64-encoded-string>",
  "profile_picture_mime": "image/jpeg",
  "created_at": "2026-04-23T10:00:00Z",
  "updated_at": null
}

To render the picture in HTML:
```html
<img src="data:image/jpeg;base64,<profile_picture value>" />

---

## Project Structure

fastapi_crud/
├── main.py          # FastAPI app, all route handlers
├── database.py      # SQLAlchemy engine & session
├── models.py        # ORM User model
├── schemas.py       # Pydantic request/response schemas
├── requirements.txt
└── README.md
```
