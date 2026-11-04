from sqlalchemy.orm import Session

from app.models.anime import AnimeSubject


class AnimeService:
    """动漫数据服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_subject(self, subject_id: int):
        return self.db.query(AnimeSubject).filter(AnimeSubject.id == subject_id).first()

    def list_subjects(
        self,
        page: int = 1,
        page_size: int = 20,
        subject_type: int | None = None,
    ):
        query = self.db.query(AnimeSubject)
        if subject_type is not None:
            query = query.filter(AnimeSubject.subject_type == subject_type)
        total = query.count()
        data = query.offset((page - 1) * page_size).limit(page_size).all()
        return data, total
