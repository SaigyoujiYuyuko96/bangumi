from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnimeSubjectBase(BaseModel):
    bgm_id: int
    name: str
    name_cn: Optional[str] = None
    name_en: Optional[str] = None
    summary: Optional[str] = None
    subject_type: int
    platform: Optional[str] = None
    total_episodes: int = 0
    status: Optional[str] = None
    air_date: Optional[date] = None
    end_date: Optional[date] = None
    season: Optional[str] = None
    year: Optional[int] = None
    rating_score: Optional[float] = None
    rating_rank: Optional[int] = None
    rating_total: Optional[int] = None
    image: Optional[Dict[str, Any]] = None
    tags: Optional[List[Dict[str, Any]]] = None
    url: Optional[str] = None


class AnimeSubject(AnimeSubjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnimeSubjectListItem(BaseModel):
    id: int
    bgm_id: int
    name: str
    name_cn: Optional[str] = None
    subject_type: int
    year: Optional[int] = None
    rating_score: Optional[float] = None
    rating_rank: Optional[int] = None
    image: Optional[Dict[str, Any]] = None
    tags: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class AnimeEpisodeBase(BaseModel):
    bgm_id: int
    subject_id: int
    name: Optional[str] = None
    name_cn: Optional[str] = None
    ep: Optional[int] = None
    sort: Optional[int] = None
    episode_type: Optional[int] = None
    duration: Optional[str] = None
    airdate: Optional[date] = None
    desc: Optional[str] = None


class AnimeEpisode(AnimeEpisodeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnimeCharacterBase(BaseModel):
    bgm_id: int
    name: str
    name_cn: Optional[str] = None
    role: Optional[str] = None
    image: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class AnimeCharacter(AnimeCharacterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnimePersonBase(BaseModel):
    bgm_id: int
    name: str
    name_cn: Optional[str] = None
    type: Optional[int] = None
    career: Optional[List[str]] = None
    image: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class AnimePerson(AnimePersonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
