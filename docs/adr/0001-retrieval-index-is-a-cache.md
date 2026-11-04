# Retrieval index is a rebuildable cache, not a second source of truth

Semantic search needs vectors; the application already keeps every Subject in
relational tables. Rather than duplicating Subject data into a vector store, the
index holds only a Subject's `bgm_id` and its vector. A search returns `bgm_id`s,
which are then loaded from the relational store.

The vector store is therefore disposable: deleting its directory and rebuilding
it from the relational tables loses nothing. Two writable copies of the same
records would drift apart, and a drift between a search result and the record it
points at is the kind of bug that takes a day to notice and an hour to explain.

Considered and rejected: making the vector store the primary store for Subjects
(it would force every browse and filter query through a vector API), and storing
Subject text alongside its vector (a cache that silently answers with stale text
after an edit).

Consequence worth knowing: a Subject edited in the relational store is findable
by its old text until the index is rebuilt. Any write path that changes
searchable text must refresh that Subject's entry.
