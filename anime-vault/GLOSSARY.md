# AnimeVault

An anime knowledge-base application: it stores works pulled from Bangumi, tracks
what a user intends to watch, and answers questions about the catalogue by
meaning rather than by keyword.

## Language

### Catalogue

**Subject**:
A single catalogued work — an anime, manga, game, music release, or live-action
title. The unit everything else hangs off.
_Avoid_: Item, entry, work, title

**Anime**:
A Subject whose kind is animation. A narrower term than Subject; not a synonym.
_Avoid_: Show, series, 番 (when the general case is meant)

**Episode**:
One instalment of an Anime, identified by its ordering within the Subject.
_Avoid_: Chapter, part, instalment

**Character**:
A fictional person appearing within a Subject.
_Avoid_: Role, cast member

**Person**:
A real individual credited on a Subject — a voice actor, director, or writer.
Distinct from Character: one is depicted, the other is credited.
_Avoid_: Staff, contributor, member

### Collection

**Collection**:
A user's stated relationship to one Subject, carrying an intent, a progress
marker, and optionally a score. A user has at most one Collection per Subject.
_Avoid_: Favourite, bookmark, library item, entry

**Intent**:
What the user means to do with a Subject — wish to watch, watching, watched,
on hold, or dropped. The intent is the user's plan; progress is how far it got.
_Avoid_: Status, state, list

**Progress**:
How much of an Anime's Episodes the user has actually seen. Independent of
Intent: a dropped Subject still has a Progress.
_Avoid_: Position, watched count

### Retrieval

**Semantic search**:
Finding Subjects by what a question means, so that "something that makes you
cry" reaches a Subject whose text never uses the word "cry". Contrasts with
keyword search, which matches the words present in the text.
_Avoid_: Vector search, similarity search, fuzzy search

**Corpus**:
The set of Subjects eligible to be found by semantic search. A Subject outside
the Corpus is invisible to it no matter how well it matches.
_Avoid_: Index, dataset, documents
