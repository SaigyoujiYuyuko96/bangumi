"""Agent 工具集 - 提供动漫相关的各种工具函数"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from app.core.database import SessionLocal
from app.models.anime import AnimeSubject, UserCollection
from app.models.user import User


@tool
def search_subjects(
    keyword: str,
    subject_type: int = 2,
    limit: int = 10,
    sort_by: str = "rating_rank",
) -> List[Dict[str, Any]]:
    """
    搜索动漫条目。

    参数:
        keyword: 搜索关键词（标题、中文名、英文名）
        subject_type: 条目类型，2=动画，1=漫画，4=游戏，3=音乐，6=三次元
        limit: 返回数量限制，默认10
        sort_by: 排序方式，rating_rank/rating_score/collect_count/air_date

    返回:
        匹配的动漫条目列表
    """
    db = SessionLocal()
    try:
        query = db.query(AnimeSubject).filter(
            (AnimeSubject.name_cn.ilike(f"%{keyword}%"))
            | (AnimeSubject.name.ilike(f"%{keyword}%"))
            | (AnimeSubject.name_en.ilike(f"%{keyword}%"))
        )

        if subject_type:
            query = query.filter(AnimeSubject.subject_type == subject_type)

        sort_columns = {
            "rating_rank": AnimeSubject.rating_rank,
            "rating_score": AnimeSubject.rating_score.desc(),
            "collect_count": AnimeSubject.collect_count.desc(),
            "air_date": AnimeSubject.air_date.desc(),
        }
        sort_col = sort_columns.get(sort_by, AnimeSubject.rating_rank)
        query = query.order_by(sort_col)

        results = query.limit(limit).all()

        return [
            {
                "id": r.id,
                "bgm_id": r.bgm_id,
                "name": r.name,
                "name_cn": r.name_cn,
                "year": r.year,
                "rating_score": r.rating_score,
                "rating_rank": r.rating_rank,
                "image": r.image,
                "tags": r.tags,
            }
            for r in results
        ]
    finally:
        db.close()


@tool
def get_subject_detail(subject_id: int) -> Dict[str, Any]:
    """
    获取动漫条目详细信息。

    参数:
        subject_id: 条目 ID

    返回:
        条目详细信息
    """
    db = SessionLocal()
    try:
        subject = db.query(AnimeSubject).filter(AnimeSubject.id == subject_id).first()
        if not subject:
            return {"error": "条目不存在"}

        return {
            "id": subject.id,
            "bgm_id": subject.bgm_id,
            "name": subject.name,
            "name_cn": subject.name_cn,
            "name_en": subject.name_en,
            "summary": subject.summary,
            "subject_type": subject.subject_type,
            "year": subject.year,
            "season": subject.season,
            "total_episodes": subject.total_episodes,
            "status": subject.status,
            "rating_score": subject.rating_score,
            "rating_rank": subject.rating_rank,
            "rating_total": subject.rating_total,
            "image": subject.image,
            "tags": subject.tags,
            "genres": subject.genres,
            "studios": subject.studios,
        }
    finally:
        db.close()


@tool
def get_trending_anime(limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取热门动漫列表。

    参数:
        limit: 返回数量限制

    返回:
        热门动漫列表
    """
    db = SessionLocal()
    try:
        results = (
            db.query(AnimeSubject)
            .filter(AnimeSubject.subject_type == 2)
            .order_by(AnimeSubject.collect_count.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": r.id,
                "name": r.name,
                "name_cn": r.name_cn,
                "year": r.year,
                "rating_score": r.rating_score,
                "rating_rank": r.rating_rank,
                "image": r.image,
            }
            for r in results
        ]
    finally:
        db.close()


@tool
def get_user_collection(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取用户的收藏列表。

    参数:
        user_id: 用户 ID
        status: 收藏状态，wish/collect/doing/on_hold/dropped

    返回:
        收藏列表
    """
    db = SessionLocal()
    try:
        query = db.query(UserCollection).filter(UserCollection.user_id == user_id)

        if status:
            query = query.filter(UserCollection.status == status)

        collections = query.order_by(UserCollection.updated_at.desc()).all()

        result = []
        for col in collections:
            subject = col.subject
            if subject:
                result.append(
                    {
                        "collection_id": col.id,
                        "subject_id": subject.id,
                        "name": subject.name,
                        "name_cn": subject.name_cn,
                        "status": col.status,
                        "rate": col.rate,
                        "ep_status": col.ep_status,
                        "image": subject.image,
                    }
                )
        return result
    finally:
        db.close()


@tool
def update_collection(
    user_id: int,
    subject_id: int,
    status: Optional[str] = None,
    rate: Optional[int] = None,
    ep_status: Optional[int] = None,
    comment: Optional[str] = None,
) -> Dict[str, Any]:
    """
    更新用户的收藏状态。

    参数:
        user_id: 用户 ID
        subject_id: 条目 ID
        status: 收藏状态，wish/collect/doing/on_hold/dropped
        rate: 评分 0-10
        ep_status: 观看集数
        comment: 短评

    返回:
        更新结果
    """
    db = SessionLocal()
    try:
        collection = (
            db.query(UserCollection)
            .filter(
                UserCollection.user_id == user_id,
                UserCollection.subject_id == subject_id,
            )
            .first()
        )

        if not collection:
            subject = db.query(AnimeSubject).filter(AnimeSubject.id == subject_id).first()
            if not subject:
                return {"error": "条目不存在"}

            collection = UserCollection(
                user_id=user_id,
                subject_id=subject_id,
                status=status or "wish",
            )
            db.add(collection)

        if status is not None:
            collection.status = status
        if rate is not None:
            collection.rate = rate
        if ep_status is not None:
            collection.ep_status = ep_status
        if comment is not None:
            collection.comment = comment

        db.commit()
        db.refresh(collection)

        return {
            "success": True,
            "collection_id": collection.id,
            "status": collection.status,
            "message": "收藏更新成功",
        }
    finally:
        db.close()


@tool
def get_calendar() -> Dict[str, List]:
    """
    获取今日放送日历。

    返回:
        按星期几分组的动漫列表
    """
    db = SessionLocal()
    try:
        results = (
            db.query(AnimeSubject)
            .filter(
                AnimeSubject.subject_type == 2,
                AnimeSubject.status == "airing",
            )
            .order_by(AnimeSubject.air_date.desc())
            .limit(50)
            .all()
        )

        return {
            "message": "放送日历功能开发中",
            "total": len(results),
        }
    finally:
        db.close()


def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    获取用户的统计数据。

    参数:
        user_id: 用户 ID

    返回:
        用户统计数据
    """
    db = SessionLocal()
    try:
        collections = db.query(UserCollection).filter(UserCollection.user_id == user_id).all()

        stats = {
            "total": len(collections),
            "wish": 0,
            "doing": 0,
            "collect": 0,
            "on_hold": 0,
            "dropped": 0,
            "total_score": 0,
            "scored_count": 0,
        }

        for col in collections:
            if col.status in stats:
                stats[col.status] += 1
            if col.rate:
                stats["total_score"] += col.rate
                stats["scored_count"] += 1

        if stats["scored_count"] > 0:
            stats["avg_score"] = round(stats["total_score"] / stats["scored_count"], 1)
        else:
            stats["avg_score"] = 0

        return stats
    finally:
        db.close()


@tool
def semantic_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    按含义搜索动漫条目。

    与 search_subjects 的区别：search_subjects 只匹配标题里的字面词，
    这个工具匹配描述的含义。问"让人哭的动画"时，标题里没有"哭"字的条目
    也能被找到。

    参数:
        query: 描述你想要什么，用自然语言，例如"催泪的青春校园故事"
        limit: 返回数量限制，默认5

    返回:
        按相关度排序的条目列表，附带相关度分数（越小越相关）
    """
    from app.services.semantic_search import get_semantic_search

    index = get_semantic_search()
    hits = index.search(query, k=limit)
    if not hits:
        return []

    db = SessionLocal()
    try:
        by_bgm_id = {h["bgm_id"]: h for h in hits}
        subjects = (
            db.query(AnimeSubject)
            .filter(AnimeSubject.bgm_id.in_(list(by_bgm_id)))
            .all()
        )
        # Preserve relevance order from the index; the SQL query has none.
        order = [h["bgm_id"] for h in hits]
        ranked = sorted(subjects, key=lambda s: order.index(s.bgm_id))

        return [
            {
                "id": s.id,
                "bgm_id": s.bgm_id,
                "name": s.name,
                "name_cn": s.name_cn,
                "year": s.year,
                "rating_score": s.rating_score,
                "rating_rank": s.rating_rank,
                "image": s.image,
                "tags": s.tags,
                "summary": s.summary,
                "relevance": by_bgm_id[s.bgm_id]["distance"],
            }
            for s in ranked
        ]
    finally:
        db.close()
