from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User

router = APIRouter(prefix="/recommend", tags=["推荐"])


@router.get("/personal")
def personal_recommend(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """个性化推荐"""
    return {"message": "Personal recommend endpoint - coming soon"}


@router.get("/similar/{id}")
def similar_recommend(id: int, db: Session = Depends(get_db)):
    """相似推荐"""
    return {"message": "Similar recommend endpoint - coming soon"}


@router.get("/season")
def season_recommend(db: Session = Depends(get_db)):
    """季度新番推荐"""
    return {"message": "Season recommend endpoint - coming soon"}


@router.get("/popular")
def popular_recommend(db: Session = Depends(get_db)):
    """热门推荐"""
    return {"message": "Popular recommend endpoint - coming soon"}
