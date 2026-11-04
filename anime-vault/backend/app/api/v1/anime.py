from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.anime import AnimeSubject, AnimeSubjectCharacter, AnimeSubjectPerson
from app.schemas.anime import AnimeEpisode, AnimeSubject as AnimeSubjectSchema, AnimeSubjectListItem
from app.schemas.common import PageResult

router = APIRouter(prefix="/anime", tags=["动漫条目"])


@router.get("", response_model=PageResult[AnimeSubjectListItem])
def list_anime(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    subject_type: Optional[int] = None,
    status: Optional[str] = None,
    year: Optional[int] = None,
    season: Optional[str] = None,
    sort_by: str = Query("rating_rank", pattern="^(rating_rank|popularity|air_date|rating_score)$"),
    db: Session = Depends(get_db),
):
    """获取动漫条目列表"""
    query = db.query(AnimeSubject)

    if subject_type is not None:
        query = query.filter(AnimeSubject.subject_type == subject_type)
    if status:
        query = query.filter(AnimeSubject.status == status)
    if year:
        query = query.filter(AnimeSubject.year == year)
    if season:
        query = query.filter(AnimeSubject.season == season)

    total = query.count()

    sort_column = {
        "rating_rank": AnimeSubject.rating_rank,
        "popularity": AnimeSubject.collect_count.desc(),
        "air_date": AnimeSubject.air_date.desc(),
        "rating_score": AnimeSubject.rating_score.desc(),
    }.get(sort_by, AnimeSubject.rating_rank)

    query = query.order_by(sort_column)
    data = query.offset((page - 1) * page_size).limit(page_size).all()

    return PageResult(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/trending", response_model=list[AnimeSubjectListItem])
def get_trending(db: Session = Depends(get_db), limit: int = Query(10, ge=1, le=50)):
    """获取热门趋势"""
    data = db.query(AnimeSubject).order_by(AnimeSubject.collect_count.desc()).limit(limit).all()
    return data


@router.get("/calendar")
def get_calendar(db: Session = Depends(get_db)):
    """获取放送日历"""
    from app.providers.bangumi import BangumiClient

    client = BangumiClient()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    calendar = loop.run_until_complete(client.get_calendar())
    loop.run_until_complete(client.close())

    result = []
    for day in calendar:
        for item in day.get("items", []):
            result.append({
                "weekday": day.get("weekday", {}).get("cn", ""),
                "id": item.get("id"),
                "name": item.get("name"),
                "name_cn": item.get("name_cn"),
                "image": item.get("images", {}).get("large"),
            })
    return result


@router.get("/{anime_id}", response_model=AnimeSubjectSchema)
def get_anime(anime_id: int, db: Session = Depends(get_db)):
    """获取动漫详情"""
    subject = db.query(AnimeSubject).filter(AnimeSubject.id == anime_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Anime not found")
    return subject


@router.get("/{anime_id}/episodes", response_model=list[AnimeEpisode])
def get_anime_episodes(anime_id: int, db: Session = Depends(get_db)):
    """获取动漫剧集列表"""
    subject = db.query(AnimeSubject).filter(AnimeSubject.id == anime_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Anime not found")
    return subject.episodes


@router.get("/{anime_id}/characters")
def get_anime_characters(anime_id: int, db: Session = Depends(get_db)):
    """获取动漫角色列表"""
    relations = (
        db.query(AnimeSubjectCharacter)
        .filter(AnimeSubjectCharacter.subject_id == anime_id)
        .order_by(AnimeSubjectCharacter.order_index)
        .all()
    )

    from app.models.anime import AnimeCharacter
    result = []
    for rel in relations:
        character = db.query(AnimeCharacter).filter(AnimeCharacter.id == rel.character_id).first()
        if character:
            result.append({
                "id": character.id,
                "bgm_id": character.bgm_id,
                "name": character.name,
                "name_cn": character.name_cn,
                "role": rel.role,
                "image": character.image,
                "summary": character.summary,
            })
    return result


@router.get("/{anime_id}/persons")
def get_anime_persons(anime_id: int, db: Session = Depends(get_db)):
    """获取动漫制作人员"""
    relations = (
        db.query(AnimeSubjectPerson)
        .filter(AnimeSubjectPerson.subject_id == anime_id)
        .order_by(AnimeSubjectPerson.order_index)
        .all()
    )

    from app.models.anime import AnimePerson
    result = []
    for rel in relations:
        person = db.query(AnimePerson).filter(AnimePerson.id == rel.person_id).first()
        if person:
            result.append({
                "id": person.id,
                "bgm_id": person.bgm_id,
                "name": person.name,
                "name_cn": person.name_cn,
                "position": rel.position,
                "career": person.career,
                "image": person.image,
                "summary": person.summary,
            })
    return result


@router.get("/{anime_id}/relations")
def get_anime_relations(anime_id: int, db: Session = Depends(get_db)):
    """获取关联条目"""
    subject = db.query(AnimeSubject).filter(AnimeSubject.id == anime_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Anime not found")

    relations = subject.relations or []
    return relations
