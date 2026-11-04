"""Tests for the semantic search index and its agent tool."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.anime import AnimeSubject

# The embedding model downloads on first use (~80MB). Tests that need it are
# marked so the suite stays runnable offline.
requires_model = pytest.mark.skipif(
    __import__("os").environ.get("SKIP_EMBEDDING_TESTS") == "1",
    reason="SKIP_EMBEDDING_TESTS=1 set; embedding model not exercised",
)


def _subject(**overrides) -> AnimeSubject:
    """A Subject with only the fields build_subject_text reads."""
    defaults = dict(
        bgm_id=1,
        name="CLANNAD",
        name_cn="CLANNAD",
        subject_type=2,
        year=2007,
        total_episodes=23,
        summary="冈崎朋也在校园里遇见古河渚的故事。",
        tags=[{"name": "key", "count": 900}, {"name": "家族", "count": 800}],
    )
    defaults.update(overrides)
    return AnimeSubject(**defaults)


class TestBuildSubjectText:
    """The text that gets embedded is what search actually sees."""

    def test_includes_title_summary_and_tags(self):
        from app.services.semantic_search import build_subject_text

        text = build_subject_text(_subject())

        assert "CLANNAD" in text
        assert "冈崎朋也" in text
        assert "家族" in text

    def test_includes_year_and_episode_count(self):
        from app.services.semantic_search import build_subject_text

        text = build_subject_text(_subject(year=2007, total_episodes=23))

        assert "2007" in text
        assert "23" in text

    def test_missing_optional_fields_do_not_raise(self):
        from app.services.semantic_search import build_subject_text

        text = build_subject_text(
            _subject(year=None, total_episodes=None, summary=None, tags=None)
        )

        assert "CLANNAD" in text

    def test_tag_limit_caps_how_many_tags_reach_the_chunk(self):
        from app.services.semantic_search import build_subject_text

        many = [{"name": f"tag{i}", "count": 100 - i} for i in range(50)]
        text = build_subject_text(_subject(tags=many))

        assert "tag0" in text
        assert "tag30" not in text


class TestSemanticSearchIndex:
    """Round-trip through a real chroma collection in a temp directory."""

    @pytest.fixture()
    def index(self, tmp_path, monkeypatch):
        from app.services import semantic_search as module

        monkeypatch.setattr(module, "get_semantic_search", lambda *a, **k: module.SemanticSearch(str(tmp_path)))
        return module.SemanticSearch(str(tmp_path))

    @requires_model
    def test_upsert_then_search_returns_the_same_bgm_id(self, index):
        index.upsert(42, "赛博朋克 反乌托邦 义体改造")

        hits = index.search("赛博朋克 反乌托邦 义体改造", k=1)

        assert hits[0]["bgm_id"] == 42

    @requires_model
    def test_search_results_are_ordered_by_distance(self, index):
        index.upsert_many([
            (1, "治愈 日常 校园 轻松", None),
            (2, "赛博朋克 反乌托邦 义体改造 黑客", None),
        ])

        hits = index.search("赛博朋克 义体 黑客", k=2)

        assert hits[0]["bgm_id"] == 2
        assert hits[0]["distance"] <= hits[1]["distance"]

    @requires_model
    def test_upsert_of_existing_id_replaces_rather_than_duplicates(self, index):
        index.upsert(7, "催泪 家庭 亲情")
        index.upsert(7, "热血 战斗 少年")

        hits = index.search("热血 战斗 少年", k=10)
        matching = [h for h in hits if h["bgm_id"] == 7]

        assert len(matching) == 1

    @requires_model
    def test_delete_removes_the_entry(self, index):
        index.upsert(9, "科幻 太空 歌剧")
        index.delete(9)

        hits = index.search("科幻 太空 歌剧", k=10)

        assert all(h["bgm_id"] != 9 for h in hits)

    @requires_model
    def test_empty_index_returns_no_hits(self, index):
        assert index.search("随便问点什么", k=5) == []


class TestSemanticSearchTool:
    """The tool resolves chroma hits back against the relational store."""

    @pytest.fixture()
    def db(self, tmp_path):
        engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
        AnimeSubject.__table__.create(bind=engine)
        session = sessionmaker(bind=engine)()

        session.add(_subject(bgm_id=1, name_cn="CLANNAD"))
        session.add(_subject(bgm_id=2, name_cn="赛博朋克：边缘行者", summary="夜之城的义体改造故事。"))
        session.commit()

        yield session
        session.close()

    @requires_model
    def test_tool_returns_rows_from_the_relational_store(self, db, monkeypatch, tmp_path):
        from app.agents import tools
        from app.services import semantic_search as module

        index = module.SemanticSearch(str(tmp_path / "idx"))
        index.upsert(1, "催泪 家庭 亲情 校园")
        monkeypatch.setattr(module, "get_semantic_search", lambda *a, **k: index)
        monkeypatch.setattr(tools, "SessionLocal", lambda: db)

        results = tools.semantic_search.invoke({"query": "催泪 家庭 亲情", "limit": 5})

        assert any(r["bgm_id"] == 1 for r in results)
        # Every field comes from SQLite, not from the index.
        assert any(r["name_cn"] == "CLANNAD" for r in results)

    @requires_model
    def test_tool_preserves_relevance_order_not_sql_order(self, db, monkeypatch, tmp_path):
        from app.agents import tools
        from app.services import semantic_search as module

        index = module.SemanticSearch(str(tmp_path / "idx"))
        index.upsert(1, "催泪 家庭 亲情")
        index.upsert(2, "赛博朋克 义体 黑客")
        monkeypatch.setattr(module, "get_semantic_search", lambda *a, **k: index)
        monkeypatch.setattr(tools, "SessionLocal", lambda: db)

        results = tools.semantic_search.invoke({"query": "赛博朋克 义体 黑客", "limit": 2})

        assert results[0]["bgm_id"] == 2

    def test_tool_returns_empty_list_when_nothing_matches(self, db, monkeypatch):
        from app.agents import tools
        from app.services import semantic_search as module

        class Empty:
            def search(self, query, k=5):
                return []

        monkeypatch.setattr(module, "get_semantic_search", lambda *a, **k: Empty())
        monkeypatch.setattr(tools, "SessionLocal", lambda: db)

        assert tools.semantic_search.invoke({"query": "不存在的东西", "limit": 5}) == []
