from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, func, cast, String
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.anime import AnimeSubject
from app.schemas.anime import AnimeSubjectListItem
from app.schemas.common import PageResult

router = APIRouter(prefix="/search", tags=["搜索"])


@router.get("/subjects", response_model=PageResult[AnimeSubjectListItem])
def search_subjects(
    keyword: str = Query("", min_length=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    subject_type: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    season: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: str = Query("rank", pattern="^(rank|rating|popular|new|airdate)$"),
    tag: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=10),
    db: Session = Depends(get_db),
):
    """搜索动漫条目"""
    query = db.query(AnimeSubject)

    if keyword:
        keyword_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                AnimeSubject.name.ilike(keyword_pattern),
                AnimeSubject.name_cn.ilike(keyword_pattern),
                AnimeSubject.name_en.ilike(keyword_pattern),
                AnimeSubject.summary.ilike(keyword_pattern),
            )
        )

    if subject_type is not None:
        query = query.filter(AnimeSubject.subject_type == subject_type)

    if year:
        query = query.filter(AnimeSubject.year == year)

    if season:
        query = query.filter(AnimeSubject.season == season)

    if status:
        query = query.filter(AnimeSubject.status == status)

    if tag:
        query = query.filter(
            cast(AnimeSubject.tags, String).ilike(f"%{tag}%")
        )

    if min_score:
        query = query.filter(AnimeSubject.rating_score >= min_score * 10)

    total = query.count()

    sort_options = {
        "rank": AnimeSubject.rating_rank.asc().nullslast(),
        "rating": AnimeSubject.rating_score.desc().nullslast(),
        "popular": AnimeSubject.collect_count.desc().nullslast(),
        "new": AnimeSubject.air_date.desc().nullslast(),
        "airdate": AnimeSubject.air_date.desc().nullslast(),
    }
    sort_column = sort_options.get(sort_by, AnimeSubject.rating_rank.asc().nullslast())
    query = query.order_by(sort_column)

    data = query.offset((page - 1) * page_size).limit(page_size).all()

    return PageResult(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/suggest")
def search_suggest(
    keyword: str = Query("", min_length=1),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """搜索建议"""
    if not keyword:
        return {"suggestions": []}

    keyword_pattern = f"%{keyword}%"

    subjects = (
        db.query(AnimeSubject)
        .filter(
            or_(
                AnimeSubject.name.ilike(keyword_pattern),
                AnimeSubject.name_cn.ilike(keyword_pattern),
            )
        )
        .order_by(AnimeSubject.rating_rank.asc().nullslast())
        .limit(limit)
        .all()
    )

    suggestions = [
        {
            "id": s.id,
            "bgm_id": s.bgm_id,
            "name": s.name,
            "name_cn": s.name_cn,
            "image": s.image.get("common") if s.image else None,
            "type": "subject",
            "score": s.rating_score,
        }
        for s in subjects
    ]

    return {"suggestions": suggestions}


@router.get("/tags")
def get_popular_tags(
    subject_type: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取热门标签"""
    query = db.query(AnimeSubject)
    if subject_type is not None:
        query = query.filter(AnimeSubject.subject_type == subject_type)

    subjects = query.limit(200).all()

    tag_counts = {}
    for subject in subjects:
        if subject.tags:
            for tag in subject.tags:
                tag_name = tag.get("name", "")
                tag_count = tag.get("count", 1)
                if tag_name:
                    if tag_name in tag_counts:
                        tag_counts[tag_name] += tag_count
                    else:
                        tag_counts[tag_name] = tag_count

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    tags = [{"name": name, "count": count} for name, count in sorted_tags[:limit]]

    return {"tags": tags}


@router.get("/years")
def get_available_years(
    subject_type: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """获取可用年份列表"""
    query = db.query(AnimeSubject.year)
    if subject_type is not None:
        query = query.filter(AnimeSubject.subject_type == subject_type)

    years = (
        query.filter(AnimeSubject.year.isnot(None))
        .distinct()
        .order_by(AnimeSubject.year.desc())
        .all()
    )

    return {"years": [year[0] for year in years if year[0]]}


@router.get("/seasons")
def get_available_seasons(
    subject_type: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """获取可用季度列表"""
    seasons = [
        {"value": "spring", "label": "春季 (1-3月)"},
        {"value": "summer", "label": "夏季 (4-6月)"},
        {"value": "autumn", "label": "秋季 (7-9月)"},
        {"value": "winter", "label": "冬季 (10-12月)"},
    ]
    return {"seasons": seasons}
