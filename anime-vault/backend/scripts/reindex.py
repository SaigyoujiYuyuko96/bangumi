"""Build and rebuild the semantic-search index for AnimeVault subjects.

Two modes:

    python scripts/reindex.py                 # rebuild from the relational store
    python scripts/reindex.py --fetch 200     # pull top-ranked anime from Bangumi first

``--fetch`` pages the public ranking endpoint, which already carries summary and
tags, so it costs one request per 100 subjects instead of the three-per-subject
that a full ``sync_subject`` would spend. It stores the subjects relationally and
indexes them in the same pass.

The index is a cache: ``--rebuild`` wipes it and re-derives every entry from the
relational store, which is always safe. See
``docs/adr/0001-retrieval-index-is-a-cache.md`` at the workspace root.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.anime import AnimeSubject
from app.providers.bangumi import BangumiClient
from app.services.semantic_search import build_subject_text, get_semantic_search
from app.services.sync_service import SyncService

PAGE_SIZE = 100


async def fetch_and_store(limit: int, proxy: str | None, subject_type: int = 2) -> int:
    """Pull the top ``limit`` ranked subjects and persist them. Returns the count.

    ``get_top_subjects`` takes no pagination params, so this asks for the whole
    page once and slices it locally.
    """
    client = BangumiClient(proxy=proxy, timeout=30.0)
    db = SessionLocal()
    mapper = SyncService(db)
    stored = 0
    try:
        response = await client.get_top_subjects(subject_type=subject_type, limit=PAGE_SIZE)
        subjects = (response.get("data") or [])[:limit]
        if not subjects:
            return 0

        for raw in subjects:
            bgm_id = raw.get("id")
            if not bgm_id:
                continue
            existing = db.query(AnimeSubject).filter(AnimeSubject.bgm_id == bgm_id).first()
            mapped = mapper._map_subject_data(raw)
            if existing:
                for key, value in mapped.__dict__.items():
                    if key != "_sa_instance_state" and value is not None:
                        setattr(existing, key, value)
            else:
                db.add(mapped)
            stored += 1

        db.commit()
        print(f"  fetched {stored}/{limit}", flush=True)
    finally:
        await client.close()
        await mapper.close()
        db.close()
    return stored


def reindex_from_store(rebuild: bool = False) -> int:
    """Embed every subject currently in the relational store."""
    index = get_semantic_search()
    if rebuild:
        index.reset()
        print("  index reset")

    db = SessionLocal()
    try:
        subjects = db.query(AnimeSubject).all()
        entries = []
        for subject in subjects:
            text = build_subject_text(subject)
            if text.strip():
                entries.append((subject.bgm_id, text, None))
        written = index.upsert_many(entries)
        print(f"  indexed {written} of {len(subjects)} subjects")
        return written
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fetch",
        type=int,
        metavar="N",
        help="pull the top N ranked anime from Bangumi before indexing",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="wipe the index before rebuilding it",
    )
    parser.add_argument(
        "--proxy",
        default=settings.BGM_PROXY or None,
        help="HTTP proxy for Bangumi (defaults to BGM_PROXY from settings)",
    )
    args = parser.parse_args()

    if args.fetch:
        print(f"fetching top {args.fetch} anime" + (f" via {args.proxy}" if args.proxy else ""))
        stored = asyncio.run(fetch_and_store(args.fetch, args.proxy))
        print(f"  stored {stored} subjects")

    print("indexing from relational store")
    reindex_from_store(rebuild=args.rebuild)

    index = get_semantic_search()
    print(f"index now holds {index.count()} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
