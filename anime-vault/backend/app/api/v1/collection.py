from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.anime import AnimeSubject, UserCollection
from app.models.user import User
from app.schemas.collection import Collection, CollectionCreate, CollectionProgressUpdate, CollectionUpdate
from app.schemas.common import PageResult

router = APIRouter(prefix="/collections", tags=["追番管理"])


@router.get("", response_model=PageResult[dict])
def list_collections(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取我的收藏列表"""
    query = db.query(UserCollection).filter(UserCollection.user_id == current_user.id)

    if status:
        query = query.filter(UserCollection.status == status)

    total = query.count()
    collections = query.order_by(UserCollection.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for col in collections:
        subject = db.query(AnimeSubject).filter(AnimeSubject.id == col.subject_id).first()
        col_dict = {
            "id": col.id,
            "user_id": col.user_id,
            "subject_id": col.subject_id,
            "status": col.status,
            "rate": col.rate,
            "ep_status": col.ep_status,
            "vol_status": col.vol_status,
            "comment": col.comment,
            "private": col.private,
            "created_at": col.created_at,
            "updated_at": col.updated_at,
        }
        if subject:
            col_dict["subject"] = {
                "id": subject.id,
                "bgm_id": subject.bgm_id,
                "name": subject.name,
                "name_cn": subject.name_cn,
                "image": subject.image,
                "total_episodes": subject.total_episodes,
                "year": subject.year,
                "rating_score": subject.rating_score,
            }
        result.append(col_dict)

    return PageResult(data=result, total=total, page=page, page_size=page_size)


@router.get("/{subject_id}", response_model=Collection)
def get_collection(
    subject_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取收藏详情"""
    collection = (
        db.query(UserCollection)
        .filter(
            UserCollection.user_id == current_user.id,
            UserCollection.subject_id == subject_id,
        )
        .first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.put("/{subject_id}", response_model=Collection)
def upsert_collection(
    subject_id: int,
    collection_in: CollectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """添加或更新收藏"""
    subject = db.query(AnimeSubject).filter(AnimeSubject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Anime not found")

    collection = (
        db.query(UserCollection)
        .filter(
            UserCollection.user_id == current_user.id,
            UserCollection.subject_id == subject_id,
        )
        .first()
    )

    if collection:
        update_data = collection_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection, field, value)
    else:
        collection = UserCollection(
            user_id=current_user.id,
            subject_id=subject_id,
            status=collection_in.status,
            rate=collection_in.rate,
            ep_status=collection_in.ep_status,
            vol_status=collection_in.vol_status,
            comment=collection_in.comment,
            private=collection_in.private,
        )
        db.add(collection)

    db.commit()
    db.refresh(collection)
    return collection


@router.patch("/{subject_id}/progress", response_model=Collection)
def update_progress(
    subject_id: int,
    progress_in: CollectionProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新观看进度"""
    collection = (
        db.query(UserCollection)
        .filter(
            UserCollection.user_id == current_user.id,
            UserCollection.subject_id == subject_id,
        )
        .first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if progress_in.ep_status is not None:
        collection.ep_status = progress_in.ep_status
    if progress_in.vol_status is not None:
        collection.vol_status = progress_in.vol_status

    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    subject_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除收藏"""
    collection = (
        db.query(UserCollection)
        .filter(
            UserCollection.user_id == current_user.id,
            UserCollection.subject_id == subject_id,
        )
        .first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    db.delete(collection)
    db.commit()


@router.post("/sync")
def sync_bangumi(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """同步 Bangumi 收藏"""
    return {"message": "Sync endpoint - coming soon"}


@router.get("/stats")
def get_collection_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取收藏统计"""
    from sqlalchemy import func

    stats = {}
    for status in ['wish', 'doing', 'collect', 'on_hold', 'dropped']:
        count = (
            db.query(func.count(UserCollection.id))
            .filter(
                UserCollection.user_id == current_user.id,
                UserCollection.status == status,
            )
            .scalar()
        )
        stats[status] = count or 0

    return stats
