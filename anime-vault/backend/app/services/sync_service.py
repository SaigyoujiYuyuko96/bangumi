import asyncio
from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.anime import (
    AnimeCharacter,
    AnimeEpisode,
    AnimePerson,
    AnimeSubject,
    AnimeSubjectCharacter,
    AnimeSubjectPerson,
    SyncTask,
)
from app.providers.bangumi import BangumiClient


class SyncService:
    """数据同步服务"""

    def __init__(self, db: Session):
        self.db = db
        self.bangumi_client = BangumiClient(
            app_id=settings.BGM_APP_ID,
            proxy=settings.BGM_PROXY or None,
        )

    async def sync_subject(self, bgm_id: int) -> Optional[AnimeSubject]:
        """同步单个条目"""
        try:
            subject_data = await self.bangumi_client.get_subject(bgm_id)
            if not subject_data:
                return None

            existing = self.db.query(AnimeSubject).filter(AnimeSubject.bgm_id == bgm_id).first()

            subject = self._map_subject_data(subject_data)

            if existing:
                for key, value in subject.__dict__.items():
                    if key != "_sa_instance_state" and value is not None:
                        setattr(existing, key, value)
                subject = existing
            else:
                self.db.add(subject)

            self.db.commit()
            self.db.refresh(subject)

            await self.sync_episodes(subject.id, bgm_id)
            await self.sync_characters_and_persons(subject.id, bgm_id)
            self._reindex_subject(subject)

            return subject
        except Exception as e:
            self.db.rollback()
            return None

    def _reindex_subject(self, subject: AnimeSubject) -> None:
        """Refresh this Subject's entry in the semantic index.

        Syncing rewrites searchable text (summary, tags), so skipping this would
        leave search answering from the previous text -- see the ADR on the index
        being a cache. Index failures must not fail the sync itself.
        """
        try:
            from app.services.semantic_search import get_semantic_search, build_subject_text

            text = build_subject_text(subject)
            if text.strip():
                get_semantic_search().upsert(subject.bgm_id, text)
        except Exception:
            pass

    async def sync_batch_subjects(self, bgm_ids: List[int]) -> Dict[str, int]:
        """批量同步条目"""
        results = {"success": 0, "failed": 0}

        for bgm_id in bgm_ids:
            try:
                subject = await self.sync_subject(bgm_id)
                if subject:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                await asyncio.sleep(0.5)
            except Exception:
                results["failed"] += 1

        return results

    async def sync_episodes(self, subject_id: int, bgm_id: int):
        """同步剧集"""
        try:
            episodes_data = await self.bangumi_client.get_all_episodes(bgm_id)
            if not episodes_data:
                return

            existing_episodes = {
                ep.bgm_id: ep
                for ep in self.db.query(AnimeEpisode).filter(AnimeEpisode.subject_id == subject_id).all()
            }

            for episode_data in episodes_data:
                episode = self._map_episode_data(episode_data, subject_id)

                if episode.bgm_id in existing_episodes:
                    existing = existing_episodes[episode.bgm_id]
                    for key, value in episode.__dict__.items():
                        if key != "_sa_instance_state" and value is not None:
                            setattr(existing, key, value)
                else:
                    self.db.add(episode)

            self.db.commit()
        except Exception:
            self.db.rollback()

    async def sync_characters_and_persons(self, subject_id: int, bgm_id: int):
        """同步角色和人物"""
        try:
            characters_data = await self.bangumi_client.get_subject_characters(bgm_id)
            persons_data = await self.bangumi_client.get_subject_persons(bgm_id)

            if isinstance(characters_data, list) and characters_data:
                await self._sync_subject_characters(subject_id, characters_data)

            if isinstance(persons_data, list) and persons_data:
                await self._sync_subject_persons(subject_id, persons_data)

            self.db.commit()
        except Exception:
            self.db.rollback()

    async def _sync_subject_characters(self, subject_id: int, characters_data: List[Dict]):
        """同步条目角色关系"""
        existing_relations = {
            rel.character_id: rel
            for rel in self.db.query(AnimeSubjectCharacter)
            .filter(AnimeSubjectCharacter.subject_id == subject_id)
            .all()
        }

        for i, char_data in enumerate(characters_data):
            character_info = char_data.get("character", {})
            person_info = char_data.get("person", {})
            role = char_data.get("role", "")

            character_bgm_id = character_info.get("id")
            if not character_bgm_id:
                continue

            character = await self._get_or_create_character(character_bgm_id, character_info)

            if character.id in existing_relations:
                existing_relations[character.id].role = role
                existing_relations[character.id].order_index = i
            else:
                relation = AnimeSubjectCharacter(
                    subject_id=subject_id,
                    character_id=character.id,
                    role=role,
                    order_index=i,
                )
                self.db.add(relation)

    async def _sync_subject_persons(self, subject_id: int, persons_data: List[Dict]):
        """同步条目人物关系"""
        existing_relations = {}
        for rel in self.db.query(AnimeSubjectPerson).filter(AnimeSubjectPerson.subject_id == subject_id).all():
            key = (rel.person_id, rel.position)
            existing_relations[key] = rel

        for i, person_data in enumerate(persons_data):
            person_bgm_id = person_data.get("id")
            position = person_data.get("relation", "")

            if not person_bgm_id:
                continue

            person = await self._get_or_create_person(person_bgm_id, person_data)

            key = (person.id, position)
            if key in existing_relations:
                existing_relations[key].order_index = i
            else:
                relation = AnimeSubjectPerson(
                    subject_id=subject_id,
                    person_id=person.id,
                    position=position,
                    order_index=i,
                )
                self.db.add(relation)

    async def _get_or_create_character(self, bgm_id: int, data: Dict = None) -> AnimeCharacter:
        """获取或创建角色"""
        existing = self.db.query(AnimeCharacter).filter(AnimeCharacter.bgm_id == bgm_id).first()
        if existing:
            return existing

        if not data:
            data = await self.bangumi_client.get_character(bgm_id)

        character = self._map_character_data(data)
        self.db.add(character)
        self.db.flush()
        return character

    async def _get_or_create_person(self, bgm_id: int, data: Dict = None) -> AnimePerson:
        """获取或创建人物"""
        existing = self.db.query(AnimePerson).filter(AnimePerson.bgm_id == bgm_id).first()
        if existing:
            return existing

        if not data:
            data = await self.bangumi_client.get_person(bgm_id)

        person = self._map_person_data(data)
        self.db.add(person)
        self.db.flush()
        return person

    def _map_subject_data(self, data: Dict) -> AnimeSubject:
        """映射条目数据"""
        rating = data.get("rating", {})
        images = data.get("images", {})
        infobox = data.get("infobox", [])
        tags = data.get("tags", [])

        return AnimeSubject(
            bgm_id=data.get("id", 0),
            name=data.get("name", ""),
            name_cn=data.get("name_cn"),
            name_en=data.get("name_en"),
            summary=data.get("summary"),
            subject_type=data.get("type", 0),
            platform=data.get("platform"),
            total_episodes=data.get("eps", 0),
            status=data.get("status"),
            air_date=self._parse_date(data.get("air_date")),
            end_date=self._parse_date(data.get("end_date")),
            season=data.get("season"),
            year=data.get("year"),
            rating_score=round(rating.get("score", 0) * 10) if rating.get("score") else None,
            rating_rank=rating.get("rank"),
            rating_total=rating.get("total"),
            popularity_rank=data.get("popularity"),
            collect_count=data.get("collection", {}).get("collect", 0),
            doing_count=data.get("collection", {}).get("doing", 0),
            wish_count=data.get("collection", {}).get("wish", 0),
            collect_user_count=data.get("collection", {}).get("collect", 0),
            on_hold_count=data.get("collection", {}).get("on_hold", 0),
            dropped_count=data.get("collection", {}).get("dropped", 0),
            image={
                "large": images.get("large"),
                "common": images.get("common"),
                "medium": images.get("medium"),
                "small": images.get("small"),
                "grid": images.get("grid"),
            },
            infobox=[{"key": item.get("key"), "value": item.get("value")} for item in infobox] if infobox else None,
            tags=[{"name": tag.get("name"), "count": tag.get("count")} for tag in tags] if tags else None,
            genres=data.get("genres"),
            studios=data.get("studios"),
            relations=data.get("relations"),
            url=data.get("url"),
            synced_at=datetime.now(),
        )

    def _map_episode_data(self, data: Dict, subject_id: int) -> AnimeEpisode:
        """映射剧集数据"""
        return AnimeEpisode(
            bgm_id=data.get("id", 0),
            subject_id=subject_id,
            name=data.get("name"),
            name_cn=data.get("name_cn"),
            ep=data.get("ep"),
            sort=data.get("sort"),
            episode_type=data.get("type", 0),
            duration=data.get("duration"),
            airdate=self._parse_date(data.get("airdate")),
            comment=data.get("comment", 0),
            desc=data.get("desc"),
            disc=data.get("disc", 0),
        )

    def _map_character_data(self, data: Dict) -> AnimeCharacter:
        """映射角色数据"""
        images = data.get("images", {})
        return AnimeCharacter(
            bgm_id=data.get("id", 0),
            name=data.get("name", ""),
            name_cn=data.get("name_cn"),
            role=data.get("role"),
            image={
                "large": images.get("large"),
                "medium": images.get("medium"),
                "small": images.get("small"),
            },
            infobox=data.get("infobox"),
            summary=data.get("summary"),
        )

    def _map_person_data(self, data: Dict) -> AnimePerson:
        """映射人物数据"""
        images = data.get("images", {})
        return AnimePerson(
            bgm_id=data.get("id", 0),
            name=data.get("name", ""),
            name_cn=data.get("name_cn"),
            type=data.get("type"),
            career=data.get("career"),
            image={
                "large": images.get("large"),
                "medium": images.get("medium"),
                "small": images.get("small"),
            },
            infobox=data.get("infobox"),
            summary=data.get("summary"),
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    async def sync_top_anime(self, limit: int = 50) -> Dict[str, int]:
        """同步热门动画"""
        task = SyncTask(
            task_type="top_anime",
            status="running",
            total_items=limit,
            started_at=datetime.now(),
        )
        self.db.add(task)
        self.db.commit()

        try:
            result = await self.bangumi_client.get_top_subjects(subject_type=2, limit=limit)
            subjects = result.get("data", [])
            bgm_ids = [subject.get("id") for subject in subjects if subject.get("id")]

            results = await self.sync_batch_subjects(bgm_ids)

            task.status = "completed"
            task.processed_items = results["success"]
            task.failed_items = results["failed"]
            task.completed_at = datetime.now()
            self.db.commit()

            return results
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.db.commit()
            return {"success": 0, "failed": limit}

    async def sync_by_keyword(self, keyword: str, limit: int = 20) -> Dict[str, int]:
        """按关键词同步"""
        task = SyncTask(
            task_type=f"search_{keyword}",
            status="running",
            total_items=limit,
            started_at=datetime.now(),
        )
        self.db.add(task)
        self.db.commit()

        try:
            result = await self.bangumi_client.search_subjects(keyword=keyword, limit=limit)
            subjects = result.get("data", [])
            bgm_ids = [subject.get("id") for subject in subjects if subject.get("id")]

            results = await self.sync_batch_subjects(bgm_ids)

            task.status = "completed"
            task.processed_items = results["success"]
            task.failed_items = results["failed"]
            task.completed_at = datetime.now()
            self.db.commit()

            return results
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.db.commit()
            return {"success": 0, "failed": limit}

    async def sync_calendar(self) -> Dict[str, int]:
        """同步放送日历"""
        task = SyncTask(
            task_type="calendar",
            status="running",
            started_at=datetime.now(),
        )
        self.db.add(task)
        self.db.commit()

        try:
            calendar = await self.bangumi_client.get_calendar()
            bgm_ids = []
            for day in calendar:
                for item in day.get("items", []):
                    bgm_ids.append(item.get("id"))

            task.total_items = len(bgm_ids)
            results = await self.sync_batch_subjects(bgm_ids)

            task.status = "completed"
            task.processed_items = results["success"]
            task.failed_items = results["failed"]
            task.completed_at = datetime.now()
            self.db.commit()

            return results
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.db.commit()
            return {"success": 0, "failed": 0}

    def get_sync_tasks(self, page: int = 1, page_size: int = 20) -> tuple:
        """获取同步任务列表"""
        query = self.db.query(SyncTask).order_by(SyncTask.created_at.desc())
        total = query.count()
        tasks = query.offset((page - 1) * page_size).limit(page_size).all()
        return tasks, total

    def get_sync_task(self, task_id: int) -> Optional[SyncTask]:
        """获取同步任务详情"""
        return self.db.query(SyncTask).filter(SyncTask.id == task_id).first()

    async def close(self):
        """关闭客户端"""
        await self.bangumi_client.close()
