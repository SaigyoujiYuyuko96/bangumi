from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnimeSubject(Base):
    __tablename__ = "anime_subjects"

    id = Column(Integer, primary_key=True, index=True)
    bgm_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    name_cn = Column(String(500), index=True)
    name_en = Column(String(500))
    summary = Column(Text)
    subject_type = Column(Integer, nullable=False, index=True)
    platform = Column(String(100))
    total_episodes = Column(Integer, default=0)
    status = Column(String(20), index=True)
    air_date = Column(Date)
    end_date = Column(Date)
    season = Column(String(20))
    year = Column(Integer, index=True)
    rating_score = Column(Integer)
    rating_rank = Column(Integer, index=True)
    rating_total = Column(Integer)
    popularity_rank = Column(Integer)
    collect_count = Column(Integer, default=0)
    doing_count = Column(Integer, default=0)
    wish_count = Column(Integer, default=0)
    collect_user_count = Column(Integer, default=0)
    on_hold_count = Column(Integer, default=0)
    dropped_count = Column(Integer, default=0)
    image = Column(JSON)
    infobox = Column(JSON)
    tags = Column(JSON)
    genres = Column(JSON)
    studios = Column(JSON)
    relations = Column(JSON)
    url = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    synced_at = Column(DateTime(timezone=True))


class AnimeEpisode(Base):
    __tablename__ = "anime_episodes"

    id = Column(Integer, primary_key=True, index=True)
    bgm_id = Column(Integer, unique=True, nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("anime_subjects.id", ondelete="CASCADE"), index=True)
    name = Column(String(500))
    name_cn = Column(String(500))
    ep = Column(Integer)
    sort = Column(Integer)
    episode_type = Column(Integer, index=True)
    duration = Column(String(100))
    airdate = Column(Date)
    comment = Column(Integer, default=0)
    desc = Column(Text)
    disc = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subject = relationship("AnimeSubject", backref="episodes")


class AnimeCharacter(Base):
    __tablename__ = "anime_characters"

    id = Column(Integer, primary_key=True, index=True)
    bgm_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    name_cn = Column(String(200), index=True)
    role = Column(String(50))
    image = Column(JSON)
    infobox = Column(JSON)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnimePerson(Base):
    __tablename__ = "anime_persons"

    id = Column(Integer, primary_key=True, index=True)
    bgm_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    name_cn = Column(String(200), index=True)
    type = Column(Integer)
    career = Column(JSON)
    image = Column(JSON)
    infobox = Column(JSON)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnimeSubjectCharacter(Base):
    __tablename__ = "anime_subject_characters"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("anime_subjects.id", ondelete="CASCADE"), index=True)
    character_id = Column(Integer, ForeignKey("anime_characters.id", ondelete="CASCADE"), index=True)
    role = Column(String(50))
    order_index = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("subject_id", "character_id"),)


class AnimeSubjectPerson(Base):
    __tablename__ = "anime_subject_persons"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("anime_subjects.id", ondelete="CASCADE"), index=True)
    person_id = Column(Integer, ForeignKey("anime_persons.id", ondelete="CASCADE"), index=True)
    position = Column(String(100))
    order_index = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("subject_id", "person_id", "position"),)


class UserCollection(Base):
    __tablename__ = "user_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id = Column(Integer, ForeignKey("anime_subjects.id", ondelete="CASCADE"), index=True)
    status = Column(String(20), nullable=False, index=True)
    rate = Column(Integer)
    ep_status = Column(Integer, default=0)
    vol_status = Column(Integer, default=0)
    tags = Column(JSON)
    comment = Column(Text)
    private = Column(Boolean, default=False)
    bgm_updated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("user_id", "subject_id"),)

    subject = relationship("AnimeSubject")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    message_meta = Column(JSON)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SyncTask(Base):
    __tablename__ = "sync_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
