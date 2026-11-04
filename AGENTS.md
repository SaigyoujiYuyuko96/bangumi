# AGENTS.md

Guidance for coding agents working in this repository.

## Repository shape

This is a multi-project workspace rooted at `D:\01_开发项目\bangumi`, tracking research and scaffolding for a Bangumi-related anime data tool.

- `anime-vault/` — the main application. FastAPI backend (`backend/app`, SQLAlchemy + Alembic, SQLite `animevault.db`), React + Vite + TypeScript + Tailwind frontend (`frontend/src`), nginx reverse proxy, Docker Compose for dev and prod.
- `bgm-cli/` — a **separate upstream checkout** (its own git repository, remote `aronnaxlin/bgm-cli`). Git-ignored here; treat it as a reference implementation, not part of this repo's source.
- `anime-vault-proposal.md` — the design proposal that `anime-vault/` implements.
- `scripts/` — local setup helpers (e.g. the gh CLI bootstrap wizard).

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in `SaigyoujiYuyuko96/bangumi`, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles use their default label strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), all of which exist in the repo. See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context: a root `GLOSSARY-MAP.md` indexes one `GLOSSARY.md` per sub-project, with `docs/adr/` for decisions. See `docs/agents/domain.md`.

## Environment notes

- Primary shell for agent tooling on this machine is Cygwin bash; Windows paths need `cygpath` when mixing.
- `github.com` over plain HTTPS times out on this network while `api.github.com` works directly. Git network operations (`fetch`/`push`/`clone`) against GitHub need an HTTP proxy: `HTTPS_PROXY=http://127.0.0.1:10808 NO_PROXY=api.github.com,localhost,127.0.0.1`. Do not write these into global environment variables — pass them per-command.
- `gh` is installed at `C:\Program Files\GitHub CLI\gh.exe` and authenticated as `SaigyoujiYuyuko96`.
