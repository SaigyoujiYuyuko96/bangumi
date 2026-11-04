from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user, get_db
from app.models.user import User
from app.services.sync_service import SyncService

router = APIRouter(prefix="/admin", tags=["管理后台"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """获取统计数据"""
    from app.models.anime import AnimeSubject, AnimeEpisode, AnimeCharacter, AnimePerson

    stats = {
        "subjects": db.query(AnimeSubject).count(),
        "episodes": db.query(AnimeEpisode).count(),
        "characters": db.query(AnimeCharacter).count(),
        "persons": db.query(AnimePerson).count(),
    }
    return stats


@router.post("/sync/top-anime")
async def sync_top_anime(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """同步热门动画"""
    sync_service = SyncService(db)
    try:
        result = await sync_service.sync_top_anime(limit=limit)
        return {"message": f"同步完成", **result}
    finally:
        await sync_service.close()


@router.post("/sync/keyword")
async def sync_by_keyword(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """按关键词同步"""
    sync_service = SyncService(db)
    try:
        result = await sync_service.sync_by_keyword(keyword=keyword, limit=limit)
        return {"message": f"关键词 '{keyword}' 同步完成", **result}
    finally:
        await sync_service.close()


@router.post("/sync/calendar")
async def sync_calendar(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """同步放送日历"""
    sync_service = SyncService(db)
    try:
        result = await sync_service.sync_calendar()
        return {"message": "放送日历同步完成", **result}
    finally:
        await sync_service.close()


@router.post("/sync/subject/{bgm_id}")
async def sync_single_subject(
    bgm_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """同步单个条目"""
    sync_service = SyncService(db)
    try:
        subject = await sync_service.sync_subject(bgm_id)
        if subject:
            return {
                "message": "同步成功",
                "subject": {
                    "id": subject.id,
                    "bgm_id": subject.bgm_id,
                    "name": subject.name,
                    "name_cn": subject.name_cn,
                },
            }
        else:
            return {"message": "同步失败"}
    finally:
        await sync_service.close()


@router.get("/sync/tasks")
def list_sync_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """同步任务列表"""
    sync_service = SyncService(db)
    tasks, total = sync_service.get_sync_tasks(page=page, page_size=page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": task.id,
                "task_type": task.task_type,
                "status": task.status,
                "total_items": task.total_items,
                "processed_items": task.processed_items,
                "failed_items": task.failed_items,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
            }
            for task in tasks
        ],
    }


@router.get("/sync/tasks/{task_id}")
def get_sync_task(
    task_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """同步任务详情"""
    sync_service = SyncService(db)
    task = sync_service.get_sync_task(task_id)
    if not task:
        return {"error": "任务不存在"}
    return {
        "id": task.id,
        "task_type": task.task_type,
        "status": task.status,
        "total_items": task.total_items,
        "processed_items": task.processed_items,
        "failed_items": task.failed_items,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "error_message": task.error_message,
    }


@router.get("/users")
def list_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """用户列表"""
    from app.models.user import User as UserModel

    users = db.query(UserModel).all()
    return {
        "total": len(users),
        "items": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in users
        ],
    }
