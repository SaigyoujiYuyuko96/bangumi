from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    avatar_url = Column(String(1000))
    bio = Column(Text)
    bgm_user_id = Column(Integer, unique=True, index=True)
    bgm_username = Column(String(50))
    bgm_access_token = Column(String(255))
    bgm_refresh_token = Column(String(255))
    bgm_token_expires_at = Column(DateTime(timezone=True))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
