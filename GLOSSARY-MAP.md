# Glossary Map

This workspace holds more than one body of language: an application with its own
domain vocabulary, plus an upstream checkout kept only as reference.

## Contexts

- [AnimeVault](./anime-vault/GLOSSARY.md): the anime knowledge-base application —
  subjects, collections, and semantic retrieval over them.
- `bgm-cli/` — an upstream checkout of `aronnaxlin/bgm-cli`. Git-ignored and
  read-only here. No glossary: its language is not ours to define.

## Relationships

- **AnimeVault ← bgm-cli**: AnimeVault borrows the Bangumi data model that
  `bgm-cli` also speaks, but owns its own vocabulary. Where the two diverge,
  AnimeVault's glossary wins inside `anime-vault/`.
