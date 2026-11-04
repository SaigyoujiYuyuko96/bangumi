import httpx
from typing import Dict, List, Optional


class BangumiClient:
    """Bangumi API 客户端"""

    BASE_URL = "https://api.bgm.tv"
    PRIVATE_BASE_URL = "https://next.bgm.tv"

    def __init__(
        self,
        app_id: str = "",
        access_token: str = "",
        proxy: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.app_id = app_id
        self.access_token = access_token
        self.proxy = proxy
        # trust_env=False keeps a stray shell-level HTTP(S)_PROXY from silently
        # hijacking these calls; the proxy is opted into per-client instead.
        self.client = httpx.AsyncClient(
            timeout=timeout,
            proxy=proxy,
            trust_env=False,
        )

    async def get_subject(self, subject_id: int):
        """获取条目详情"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/subjects/{subject_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_subjects_by_ids(self, subject_ids: List[int]) -> List[Dict]:
        """批量获取条目详情"""
        results = []
        for subject_id in subject_ids:
            try:
                subject = await self.get_subject(subject_id)
                results.append(subject)
            except Exception:
                continue
        return results

    async def search_subjects(self, keyword: str, limit: int = 10, offset: int = 0):
        """搜索条目"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/subjects",
            params={"keyword": keyword, "limit": limit, "offset": offset},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_episodes(self, subject_id: int, limit: int = 50, offset: int = 0):
        """获取剧集列表"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/episodes",
            params={"subject_id": subject_id, "limit": limit, "offset": offset},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_all_episodes(self, subject_id: int) -> List[Dict]:
        """获取所有剧集"""
        episodes = []
        offset = 0
        while True:
            data = await self.get_episodes(subject_id, limit=50, offset=offset)
            if not data.get("data"):
                break
            episodes.extend(data["data"])
            if len(data["data"]) < 50:
                break
            offset += 50
        return episodes

    async def get_subject_characters(self, subject_id: int):
        """获取条目角色列表"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/subjects/{subject_id}/characters",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_subject_persons(self, subject_id: int):
        """获取条目人物列表"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/subjects/{subject_id}/persons",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_character(self, character_id: int):
        """获取角色详情"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/characters/{character_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_person(self, person_id: int):
        """获取人物详情"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/persons/{person_id}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_calendar(self):
        """获取放送日历"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/calendar",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def get_top_subjects(self, subject_type: int = 2, limit: int = 100):
        """获取热门条目"""
        headers = self._get_headers()
        response = await self.client.get(
            f"{self.BASE_URL}/v0/subjects",
            params={"type": subject_type, "sort": "rank", "limit": limit},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def _get_headers(self) -> dict:
        headers = {
            "User-Agent": "AnimeVault/0.1.0",
            "Accept": "application/json",
        }
        if self.app_id:
            headers["Authorization"] = f"Bearer {self.app_id}"
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def close(self):
        await self.client.aclose()
