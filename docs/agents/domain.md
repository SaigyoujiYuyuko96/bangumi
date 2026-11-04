# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

**Layout: multi-context.** This repo holds several sub-projects, each with its own vocabulary, so glossary entries live per context rather than in one flat root file.

## Before exploring, read these

- **`GLOSSARY-MAP.md`** at the repo root if it exists: it points at one `GLOSSARY.md` per context. Read each one relevant to the topic.
- **`GLOSSARY.md`** at the repo root, if it exists: root-level terms shared across contexts.
- **`docs/adr/`**: read ADRs that touch the area you're about to work in. In multi-context repos, also check the per-context `docs/adr/` directory (e.g. `anime-vault/docs/adr/`, `bgm-cli/docs/adr/`) for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

> **Current state**: none of the glossary files exist yet. `GLOSSARY-MAP.md` and the per-context `GLOSSARY.md` files are created the first time a real term gets written down — at which point the root `GLOSSARY-MAP.md` becomes the index pointing at them. Do not scaffold empty glossary files in advance.

## File structure

Multi-context repo (presence of `GLOSSARY-MAP.md` at the root):

```
/
├── GLOSSARY-MAP.md                     ← index: which context lives where
├── docs/adr/                           ← system-wide decisions
├── anime-vault/
│   ├── GLOSSARY.md
│   └── docs/adr/                       ← context-specific decisions
└── bgm-cli/
    ├── GLOSSARY.md
    └── docs/adr/
```

`bgm-cli/` is an independent upstream checkout (its own git repository, remote `aronnaxlin/bgm-cli`) and is git-ignored here, so it is a consumer reference rather than a context this repo authors. Treat its glossary as read-only background if one ever appears.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in the relevant `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
