"""Semantic search over the anime catalogue.

The index here is a cache, not a second source of truth: it stores a Subject's
``bgm_id`` and the text used to embed it, never the Subject's own fields. Callers
resolve returned ids against the relational store, so editing a Subject can never
leave a stale copy of its data reachable through search.

See ``docs/adr/0001-retrieval-index-is-a-cache.md`` at the workspace root.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "anime_subjects"

# Chroma's built-in default (all-MiniLM-L6-v2) is English-only: on Chinese text it
# scored an unrelated music anime above a cyberpunk one, so it cannot rank this
# catalogue. This model is Chinese-native and runs through the onnxruntime that
# chromadb already depends on.
EMBEDDING_MODEL = "jinaai/jina-embeddings-v2-base-zh"


def _embedding_function():
    """Lazily build the Chinese embedder.

    Imported inside the function so that merely importing this module (during an
    Alembic run, for instance) does not pull in fastembed or download a model.
    """
    from fastembed import TextEmbedding

    return TextEmbedding(EMBEDDING_MODEL)



def build_subject_text(subject: Any) -> str:
    """Flatten one Subject into the single chunk that represents it.

    One Subject yields exactly one chunk: its summary is short enough that
    splitting would only make results harder to attribute back to a Subject.
    """
    parts: List[str] = []

    titles = [subject.name_cn, subject.name, subject.name_en]
    titles = [t for t in titles if t]
    if titles:
        parts.append("标题：" + " / ".join(titles))

    if subject.summary:
        parts.append("简介：" + subject.summary)

    tag_names = _tag_names(subject.tags)
    if tag_names:
        parts.append("标签：" + "、".join(tag_names))

    if subject.genres:
        genres = subject.genres if isinstance(subject.genres, list) else []
        genre_names = [g for g in genres if isinstance(g, str) and g]
        if genre_names:
            parts.append("类型：" + "、".join(genre_names))

    if subject.studios:
        studios = subject.studios if isinstance(subject.studios, list) else []
        studio_names = [s for s in studios if isinstance(s, str) and s]
        if studio_names:
            parts.append("制作：" + "、".join(studio_names))

    if subject.year:
        parts.append(f"年份：{subject.year}")
    if subject.total_episodes:
        parts.append(f"话数：{subject.total_episodes}")

    return "\n".join(parts)


def _tag_names(tags: Any, limit: int = 20) -> List[str]:
    """Tag names, most-applied first — the long tail is noise for retrieval."""
    if not isinstance(tags, list):
        return []
    names: List[str] = []
    for tag in tags:
        if isinstance(tag, dict):
            name = tag.get("name")
        else:
            name = tag
        if isinstance(name, str) and name:
            names.append(name)
    return names[:limit]


class SemanticSearch:
    """Vector index over Subjects, keyed by ``bgm_id``."""

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = COLLECTION_NAME,
    ):
        self.persist_dir = Path(persist_dir or "./chroma_db")
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
        self._embedder = None
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = _embedding_function()
        return self._embedder

    def embed(self, texts: List[str]) -> List[List[float]]:
        # fastembed yields numpy arrays; chroma wants plain Python floats, so the
        # scalars are converted rather than shunted through list() alone.
        return [[float(x) for x in vector] for vector in self.embedder.embed(texts)]

    @property
    def collection(self):
        return self._collection

    def count(self) -> int:
        return self._collection.count()

    def upsert(
        self,
        bgm_id: int,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add or refresh one Subject's entry.

        Any write path that changes a Subject's searchable text must call this,
        otherwise search keeps answering from the old text.
        """
        if not text.strip():
            return
        meta = {"bgm_id": bgm_id}
        if metadata:
            meta.update({k: v for k, v in metadata.items() if v is not None})
        self._collection.upsert(
            ids=[str(bgm_id)],
            documents=[text],
            embeddings=self.embed([text]),
            metadatas=[meta],
        )

    def upsert_many(self, entries: Iterable[tuple[int, str, Optional[Dict[str, Any]]]]) -> int:
        """Batch upsert. Returns how many entries were written."""
        ids: List[str] = []
        docs: List[str] = []
        metas: List[Dict[str, Any]] = []

        for bgm_id, text, metadata in entries:
            if not text.strip():
                continue
            meta: Dict[str, Any] = {"bgm_id": bgm_id}
            if metadata:
                meta.update({k: v for k, v in metadata.items() if v is not None})
            ids.append(str(bgm_id))
            docs.append(text)
            metas.append(meta)

        if not ids:
            return 0
        self._collection.upsert(
            ids=ids,
            documents=docs,
            embeddings=self.embed(docs),
            metadatas=metas,
        )
        return len(ids)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Return the ``k`` Subjects closest in meaning, best first.

        Each hit carries ``bgm_id``, ``distance`` and ``text`` (what was embedded,
        useful for debugging why something matched). Resolve ``bgm_id`` against the
        relational store for the Subject's actual fields.
        """
        if not query.strip() or self.count() == 0:
            return []

        result = self._collection.query(
            query_embeddings=self.embed([query]),
            n_results=max(1, k),
            include=["documents", "metadatas", "distances"],
        )

        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        dists = (result.get("distances") or [[]])[0]

        hits: List[Dict[str, Any]] = []
        for i, doc_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            bgm_id = (meta or {}).get("bgm_id")
            if bgm_id is None:
                try:
                    bgm_id = int(doc_id)
                except (TypeError, ValueError):
                    continue
            hits.append(
                {
                    "bgm_id": int(bgm_id),
                    "distance": float(dists[i]) if i < len(dists) else None,
                    "text": docs[i] if i < len(docs) else None,
                }
            )
        return hits

    def delete(self, bgm_id: int) -> None:
        self._collection.delete(ids=[str(bgm_id)])

    def reset(self) -> None:
        """Drop every entry. The index is rebuildable from the relational store."""
        self._client.delete_collection(name=self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


_instance: Optional[SemanticSearch] = None


def get_semantic_search() -> SemanticSearch:
    """Process-wide index, built lazily on first use."""
    global _instance
    if _instance is None:
        from app.core.config import settings

        _instance = SemanticSearch(persist_dir=settings.CHROMA_DIR)
    return _instance
