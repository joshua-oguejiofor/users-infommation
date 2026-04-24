# """
# schemas.py
# ----------
# Production-level Pydantic v2 data validation schemas for the blog platform database.

# Each table has a set of related schemas following this pattern:
#   - Base      : shared fields used across create/update/read
#   - Create    : fields required when inserting a new record (no id / timestamps)
#   - Update    : all fields optional so partial PATCH requests work cleanly
#   - Response  : full record returned from the DB (includes id, timestamps, etc.)

# Relationships are expressed via nested Response schemas where useful.
# """

# from __future__ import annotations

# import re
# from datetime import datetime
# from enum import Enum
# from typing import Any, Optional

# from pydantic import (
#     BaseModel,
#     ConfigDict,
#     EmailStr,
#     Field,
#     HttpUrl,
#     field_validator,
#     model_validator,
# )


# # ---------------------------------------------------------------------------
# # Shared helpers
# # ---------------------------------------------------------------------------

# def _slugify_check(value: str) -> str:
#     """Validate that a slug contains only lowercase letters, digits, and hyphens."""
#     if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
#         raise ValueError(
#             "Slug must be lowercase alphanumeric words separated by hyphens "
#             "(e.g. 'my-awesome-post')."
#         )
#     return value


# # ---------------------------------------------------------------------------
# # Enumerations
# # ---------------------------------------------------------------------------

# class AccountStatus(str, Enum):
#     """Mirrors the 'acct_status' enum defined in the database."""
#     ACTIVE = "active"
#     SUSPENDED = "suspended"
#     BANNED = "banned"
#     PENDING = "pending"


# class UserRole(str, Enum):
#     """Roles available to platform users."""
#     ADMIN = "admin"
#     EDITOR = "editor"
#     AUTHOR = "author"
#     READER = "reader"


# class PostStatus(str, Enum):
#     """Lifecycle states of a blog post."""
#     DRAFT = "draft"
#     PUBLISHED = "published"
#     ARCHIVED = "archived"
#     SCHEDULED = "scheduled"


# class NotificationType(str, Enum):
#     """Types of in-platform notifications."""
#     COMMENT = "comment"
#     LIKE = "like"
#     FOLLOW = "follow"
#     MENTION = "mention"
#     SYSTEM = "system"


# class FileType(str, Enum):
#     """Allowed media file types."""
#     IMAGE = "image"
#     VIDEO = "video"
#     DOCUMENT = "document"
#     AUDIO = "audio"


# # ---------------------------------------------------------------------------
# # Shared Pydantic config  (enables ORM mode for SQLAlchemy model compatibility)
# # ---------------------------------------------------------------------------

# class _Base(BaseModel):
#     """
#     Root base for all schemas.
#     'from_attributes=True' allows Pydantic to read data from ORM objects
#     (e.g. SQLAlchemy model instances) in addition to plain dicts.
#     """
#     model_config = ConfigDict(from_attributes=True)


# # ===========================================================================
# # USER
# # ===========================================================================

# class UserBase(_Base):
#     """Fields shared between user create and update operations."""

#     username: str = Field(
#         ...,
#         min_length=3,
#         max_length=50,
#         description="Unique, human-readable handle for the user.",
#     )
#     email: EmailStr = Field(..., description="Validated e-mail address.")
#     role: UserRole = Field(UserRole.READER, description="Permission level.")
#     acct_status: AccountStatus = Field(
#         AccountStatus.PENDING,
#         description="Current account lifecycle status.",
#     )
#     is_verified: bool = Field(False, description="Whether the email has been verified.")

#     @field_validator("username")
#     @classmethod
#     def username_alphanumeric(cls, v: str) -> str:
#         """Usernames may only contain letters, digits, and underscores."""
#         if not re.fullmatch(r"[A-Za-z0-9_]+", v):
#             raise ValueError("Username must be alphanumeric (underscores allowed).")
#         return v.lower()  # normalise to lowercase for case-insensitive uniqueness


# class UserCreate(UserBase):
#     """
#     Schema for registering a new user.
#     The plain-text password is accepted here and must be hashed
#     by the service layer before persisting.
#     """

#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=128,
#         description="Plain-text password (will be hashed before storage).",
#     )
#     password_confirm: str = Field(
#         ...,
#         description="Must match 'password' — validated at model level.",
#     )

#     @model_validator(mode="after")
#     def passwords_match(self) -> "UserCreate":
#         """Ensure the user didn't make a typo in their confirmation field."""
#         if self.password != self.password_confirm:
#             raise ValueError("'password' and 'password_confirm' do not match.")
#         return self


# class UserUpdate(_Base):
#     """
#     Partial update schema for PATCH /users/{id}.
#     Every field is optional so callers only send what changed.
#     password_hash is intentionally excluded — use a dedicated
#     change-password endpoint instead.
#     """

#     username: Optional[str] = Field(None, min_length=3, max_length=50)
#     email: Optional[EmailStr] = None
#     role: Optional[UserRole] = None
#     acct_status: Optional[AccountStatus] = None
#     is_verified: Optional[bool] = None


# class UserResponse(UserBase):
#     """
#     Schema returned to API consumers.
#     Sensitive fields (password_hash) are intentionally omitted.
#     """

#     id: int
#     created_at: datetime
#     updated_at: datetime

#     # Nested profile is included when loaded via relationship
#     profile: Optional["ProfileResponse"] = None


# # ===========================================================================
# # PROFILE
# # ===========================================================================

# class ProfileBase(_Base):
#     """Editable profile fields."""

#     bio: Optional[str] = Field(None, max_length=500)
#     avatar_url: Optional[HttpUrl] = None
#     website_url: Optional[HttpUrl] = None
#     location: Optional[str] = Field(None, max_length=100)
#     social_links: Optional[dict[str, str]] = Field(
#         None,
#         description=(
#             "Flexible JSON map of social platform → profile URL, "
#             "e.g. {'twitter': 'https://twitter.com/handle'}."
#         ),
#     )

#     @field_validator("social_links")
#     @classmethod
#     def validate_social_links(cls, v: Optional[dict[str, str]]) -> Optional[dict[str, str]]:
#         """Each social link value must be a valid URL."""
#         if v is None:
#             return v
#         url_pattern = re.compile(r"https?://\S+")
#         for platform, url in v.items():
#             if not url_pattern.match(url):
#                 raise ValueError(f"Invalid URL for platform '{platform}': {url}")
#         return v


# class ProfileCreate(ProfileBase):
#     """Create a profile record linked to a user."""
#     user_id: int = Field(..., description="FK → users.id")


# class ProfileUpdate(ProfileBase):
#     """All fields optional for partial profile edits."""
#     pass  # inherits optional-friendly fields from ProfileBase


# class ProfileResponse(ProfileBase):
#     """Full profile record as returned by the API."""
#     id: int
#     user_id: int
#     created_at: datetime
#     updated_at: datetime


# # ===========================================================================
# # CATEGORY
# # ===========================================================================

# class CategoryBase(_Base):
#     name: str = Field(..., min_length=2, max_length=100)
#     slug: str = Field(..., description="URL-safe identifier, e.g. 'web-development'.")
#     description: Optional[str] = None

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: str) -> str:
#         return _slugify_check(v)


# class CategoryCreate(CategoryBase):
#     pass


# class CategoryUpdate(_Base):
#     name: Optional[str] = Field(None, min_length=2, max_length=100)
#     slug: Optional[str] = None
#     description: Optional[str] = None

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: Optional[str]) -> Optional[str]:
#         return _slugify_check(v) if v else v


# class CategoryResponse(CategoryBase):
#     id: int
#     created_at: datetime


# # ===========================================================================
# # TAG
# # ===========================================================================

# class TagBase(_Base):
#     name: str = Field(..., min_length=1, max_length=50)
#     slug: str = Field(...)

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: str) -> str:
#         return _slugify_check(v)


# class TagCreate(TagBase):
#     pass


# class TagUpdate(_Base):
#     name: Optional[str] = Field(None, min_length=1, max_length=50)
#     slug: Optional[str] = None

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: Optional[str]) -> Optional[str]:
#         return _slugify_check(v) if v else v


# class TagResponse(TagBase):
#     id: int


# # ===========================================================================
# # POST
# # ===========================================================================

# class PostBase(_Base):
#     title: str = Field(..., min_length=5, max_length=255)
#     slug: str = Field(...)
#     content: str = Field(..., min_length=10, description="Full HTML/Markdown body.")
#     excerpt: Optional[str] = Field(None, max_length=500)
#     status: PostStatus = Field(PostStatus.DRAFT)
#     featured_image_url: Optional[HttpUrl] = None
#     published_at: Optional[datetime] = Field(
#         None,
#         description="Set when status transitions to 'published' or 'scheduled'.",
#     )

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: str) -> str:
#         return _slugify_check(v)

#     @model_validator(mode="after")
#     def scheduled_requires_published_at(self) -> "PostBase":
#         """A post with status=scheduled must include a future publish date."""
#         if self.status == PostStatus.SCHEDULED and self.published_at is None:
#             raise ValueError("'published_at' is required when status is 'scheduled'.")
#         return self


# class PostCreate(PostBase):
#     author_id: int = Field(..., description="FK → users.id")
#     # IDs of tags/categories to attach (resolved in the service layer)
#     tag_ids: list[int] = Field(default_factory=list)
#     category_ids: list[int] = Field(default_factory=list)


# class PostUpdate(_Base):
#     """Partial update — every field optional for PATCH semantics."""
#     title: Optional[str] = Field(None, min_length=5, max_length=255)
#     slug: Optional[str] = None
#     content: Optional[str] = Field(None, min_length=10)
#     excerpt: Optional[str] = Field(None, max_length=500)
#     status: Optional[PostStatus] = None
#     featured_image_url: Optional[HttpUrl] = None
#     published_at: Optional[datetime] = None
#     tag_ids: Optional[list[int]] = None
#     category_ids: Optional[list[int]] = None

#     @field_validator("slug")
#     @classmethod
#     def valid_slug(cls, v: Optional[str]) -> Optional[str]:
#         return _slugify_check(v) if v else v


# class PostResponse(PostBase):
#     id: int
#     author_id: int
#     view_count: int = 0
#     created_at: datetime
#     updated_at: datetime

#     # Hydrated relationships (populated when JOIN is performed)
#     author: Optional["UserResponse"] = None
#     tags: list[TagResponse] = []
#     categories: list[CategoryResponse] = []


# # ===========================================================================
# # COMMENT
# # ===========================================================================

# class CommentBase(_Base):
#     content: str = Field(..., min_length=1, max_length=5000)
#     is_approved: bool = Field(
#         False,
#         description="Comments require moderation approval before being visible.",
#     )


# class CommentCreate(CommentBase):
#     post_id: int = Field(..., description="FK → posts.id")
#     user_id: int = Field(..., description="FK → users.id")
#     parent_id: Optional[int] = Field(
#         None,
#         description="FK → comments.id — set for threaded/nested replies.",
#     )


# class CommentUpdate(_Base):
#     content: Optional[str] = Field(None, min_length=1, max_length=5000)
#     is_approved: Optional[bool] = None


# class CommentResponse(CommentBase):
#     id: int
#     post_id: int
#     user_id: int
#     parent_id: Optional[int] = None
#     created_at: datetime
#     updated_at: datetime

#     # Nested author info for display
#     author: Optional["UserResponse"] = None
#     # Child replies (one level deep is usually sufficient for APIs)
#     replies: list["CommentResponse"] = []


# # ===========================================================================
# # LIKE
# # ===========================================================================

# class LikeCreate(_Base):
#     """
#     Likes have no mutable fields after creation; there is no Update schema.
#     The service layer should enforce a unique constraint on (user_id, post_id).
#     """
#     user_id: int = Field(..., description="FK → users.id")
#     post_id: int = Field(..., description="FK → posts.id")


# class LikeResponse(LikeCreate):
#     id: int
#     created_at: datetime


# # ===========================================================================
# # BOOKMARK
# # ===========================================================================

# class BookmarkCreate(_Base):
#     """Like Likes, bookmarks are either present or absent — no partial updates."""
#     user_id: int = Field(..., description="FK → users.id")
#     post_id: int = Field(..., description="FK → posts.id")


# class BookmarkResponse(BookmarkCreate):
#     id: int
#     created_at: datetime

#     post: Optional["PostResponse"] = None


# # ===========================================================================
# # POST ↔ CATEGORY  (many-to-many join table)
# # ===========================================================================

# class PostCategoryCreate(_Base):
#     """
#     Represents a single row in the post_categories join table.
#     Usually managed implicitly via PostCreate.category_ids,
#     but exposed here for direct manipulation if needed.
#     """
#     post_id: int
#     category_id: int


# class PostCategoryResponse(PostCategoryCreate):
#     pass


# # ===========================================================================
# # POST ↔ TAG  (many-to-many join table)
# # ===========================================================================

# class PostTagCreate(_Base):
#     """Represents a single row in the post_tags join table."""
#     post_id: int
#     tag_id: int


# class PostTagResponse(PostTagCreate):
#     pass


# # ===========================================================================
# # PASSWORD RESET
# # ===========================================================================

# class PasswordResetCreate(_Base):
#     """
#     Issued when a user requests a password reset.
#     The token is a securely generated random string (e.g. secrets.token_urlsafe).
#     """
#     user_id: int
#     token: str = Field(..., min_length=32, description="Cryptographically secure token.")
#     expires_at: datetime = Field(..., description="Token expiry — typically 1 hour from now.")


# class PasswordResetResponse(PasswordResetCreate):
#     id: int
#     used: bool = Field(False, description="True once the token has been consumed.")


# class PasswordResetConfirm(_Base):
#     """
#     Payload sent by the user when actually resetting their password.
#     The service layer validates the token, checks expiry, and marks it used.
#     """
#     token: str = Field(..., min_length=32)
#     new_password: str = Field(..., min_length=8, max_length=128)
#     new_password_confirm: str

#     @model_validator(mode="after")
#     def passwords_match(self) -> "PasswordResetConfirm":
#         if self.new_password != self.new_password_confirm:
#             raise ValueError("Passwords do not match.")
#         return self


# # ===========================================================================
# # REFRESH TOKEN
# # ===========================================================================

# class RefreshTokenCreate(_Base):
#     """
#     Issued alongside an access token during authentication.
#     Stored hashed in production — the raw value is only returned once.
#     """
#     user_id: int
#     token: str = Field(..., min_length=32)
#     expires_at: datetime


# class RefreshTokenResponse(_Base):
#     """Returned to the caller — never includes the raw token after initial creation."""
#     id: int
#     user_id: int
#     expires_at: datetime
#     is_revoked: bool
#     created_at: datetime


# # ===========================================================================
# # NOTIFICATION
# # ===========================================================================

# class NotificationBase(_Base):
#     type: NotificationType
#     message: str = Field(..., max_length=1000)
#     is_read: bool = Field(False)


# class NotificationCreate(NotificationBase):
#     user_id: int = Field(..., description="Recipient user FK → users.id")


# class NotificationUpdate(_Base):
#     """Only the read-status is mutable after creation."""
#     is_read: bool


# class NotificationResponse(NotificationBase):
#     id: int
#     user_id: int
#     created_at: datetime


# # ===========================================================================
# # MEDIA
# # ===========================================================================

# class MediaBase(_Base):
#     url: HttpUrl = Field(..., description="Public URL of the stored file.")
#     file_type: Optional[FileType] = None


# class MediaCreate(MediaBase):
#     uploaded_by: int = Field(..., description="FK → users.id — who uploaded the file.")


# class MediaUpdate(_Base):
#     """
#     In practice media records are rarely updated;
#     the uploader may correct the file_type classification.
#     """
#     file_type: Optional[FileType] = None


# class MediaResponse(MediaBase):
#     id: int
#     uploaded_by: int
#     created_at: datetime


# # ===========================================================================
# # AUDIT LOG
# # ===========================================================================

# class AuditLogCreate(_Base):
#     """
#     Audit logs are append-only — there is no Update schema.
#     Written by the service layer whenever a significant action occurs.
#     """
#     user_id: int = Field(..., description="FK → users.id — actor who performed the action.")
#     action: str = Field(
#         ...,
#         max_length=100,
#         description="Verb describing the action, e.g. 'post.publish', 'user.ban'.",
#     )
#     entity: str = Field(
#         ...,
#         max_length=100,
#         description="Name of the affected entity/table, e.g. 'posts'.",
#     )
#     entity_id: Optional[int] = Field(
#         None,
#         description="PK of the affected row; NULL for bulk operations.",
#     )
#     # 'timestamp' is set server-side and intentionally absent from Create


# class AuditLogResponse(AuditLogCreate):
#     id: int
#     timestamp: datetime


# # ===========================================================================
# # Rebuild forward references so nested schemas resolve correctly
# # (required when schemas reference each other — e.g. CommentResponse.replies)
# # ===========================================================================

# UserResponse.model_rebuild()
# PostResponse.model_rebuild()
# CommentResponse.model_rebuild()
# BookmarkResponse.model_rebuild()
