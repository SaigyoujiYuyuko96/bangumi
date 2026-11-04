# Bangumi Anime Vault

一个动漫知识库 + 智能问答的全栈项目。数据来自 [Bangumi.tv](https://bgm.tv)，后端 FastAPI，前端 React，检索用的是**向量语义搜索**而不是标题关键词。

[English](#english) · [架构](#架构) · [跑起来](#本地跑起来) · [检索效果](#检索效果为什么值得看)

---

## 这个项目解决什么问题

想找「有什么让人哭的动画」时，关键词搜索是没用的——没有哪部番的标题里有「哭」字。传统的 `LIKE '%催泪%'` 在这个场景下命中 0 条。

这个项目并存两套检索，同一个查询对比着看：

| 查询 | 关键词 `search_subjects` | 语义 `semantic_search` |
|---|---|---|
| `催泪` / `催泪的青春校园故事` | **0 条** | 蜂蜜与四叶草 · 凉宫春日的消失 · 蜂蜜与四叶草II · 莉兹与青鸟 |
| `CLANNAD 那种让人哭的家庭故事` | 0 条 | **CLANNAD** · CLANNAD 〜AFTER STORY〜 · FLCL · 幽灵公主 |

语义检索不是把标题塞进向量库就完事：一条 Subject 会被压成一个 chunk，包含标题、简介、标签、年份、制作公司、话数。索引里**只存 `bgm_id` 和向量**，命中后回关系库取真实数据——所以改了 Subject 不会留下可以被搜到的旧文本。理由写在 [ADR-0001](docs/adr/0001-retrieval-index-is-a-cache.md)。

## 技术栈

**后端** — Python 3.12 · FastAPI 0.115 · SQLAlchemy 2.0 · Alembic · JWT 认证
**前端** — React 18 · TypeScript · Vite · TailwindCSS · Zustand · TanStack Query
**Agent** — LangChain，8 个工具（关键词搜索 / 语义搜索 / 详情 / 排行榜 / 收藏 / 进度 / 统计 / 日历）
**检索** — ChromaDB · `jinaai/jina-embeddings-v2-base-zh`（768 维，本地 ONNX 推理，不需要 GPU 也不需要 API key）

## 项目规模

- 后端 8 个路由模块 / **41 个接口**
- 前端 **6 个页面**（首页、搜索、详情、AI 对话、追番管理、登录）
- Python + TypeScript 约 **5,800 行**
- 索引了 101 条真实 Bangumi 数据（排行榜 Top 100）

## 架构

```
                  ┌──────────────┐
   React SPA ────▶│  nginx / Vite │
                  └──────┬───────┘
                         │ /api/v1
                  ┌──────▼───────┐        ┌──────────────┐
                  │   FastAPI    │───────▶│  Bangumi API │
                  └──┬────────┬──┘  httpx └──────────────┘
                     │        │
          ┌──────────▼──┐  ┌──▼─────────────┐
          │  SQLite     │  │  ChromaDB      │
          │  真相源      │  │  向量索引(缓存) │
          └─────────────┘  └────────────────┘
                     │        ▲
                     └─命中后回查─┘
```

**关系库是唯一真相源，向量库只是可重建的缓存。** 跑 `python scripts/reindex.py --rebuild` 就能从关系库重建整个索引。

## 本地跑起来

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # 默认用 SQLite，不需要装数据库
uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 能看到全部 41 个接口。

### 灌数据 + 建索引

```bash
cd backend
python scripts/reindex.py --fetch 100    # 从 Bangumi 拉 Top 100 并建索引
```

> `api.bgm.tv` 在国内部分网络下会重置直连。如果拉取超时，在 `.env` 里设 `BGM_PROXY=http://127.0.0.1:10808`（你自己的代理端口）。

### 前端

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

### 验证检索

```bash
cd backend
python -c "
from app.services.semantic_search import get_semantic_search
for h in get_semantic_search().search('催泪的青春校园故事', k=4):
    print(f\"{h['distance']:.3f}  {h['bgm_id']}\")
"
```

## 检索效果为什么值得看

换 embedding 模型是这个项目最花时间的一件事，因为**默认的那个是坏的**：

ChromaDB 自带 `all-MiniLM-L6-v2`，是纯英文模型。用中文查询「科幻 反乌托邦 赛博格」，它的打分是：

```
银魂              0.498   ← 跟赛博朋克毫无关系，却排第一
攻壳机动队2.0      0.246   ← 真正的赛博朋克，反而更远
吹响吧！上低音号    0.523   ← 音乐番
```

换成中文原生的 `jina-embeddings-v2-base-zh` 之后：

```
赛博朋克：边缘行者   0.484   ✓
攻壳机动队2 无罪    0.592   ✓
Code Geass          0.609
```

中间还试过 `BAAI/bge-small-zh-v1.5`，失败——那个仓库没有 ONNX 权重，fastembed 拉不到。

**诚实的局限：** 只问「催泪的青春校园故事」时 CLANNAD 排不进前 4，因为它的简介里没有「青春校园」这类词，讲的是家庭。没有为了刷指标去手工调。

## 目录结构

```
.
├── anime-vault/              # 主应用
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/v1/       # 8 个路由模块，41 个接口
│   │   │   ├── agents/       # LangChain Agent + 8 个工具
│   │   │   ├── services/     # 同步、语义检索
│   │   │   ├── models/       # SQLAlchemy 模型
│   │   │   └── providers/    # Bangumi API 客户端
│   │   ├── scripts/          # reindex.py 索引重建
│   │   └── tests/
│   ├── frontend/src/         # 6 个页面
│   ├── nginx/
│   └── docker-compose.yml
├── docs/
│   ├── adr/                  # 架构决策记录
│   └── agents/               # 给 AI agent 的项目约定
└── GLOSSARY-MAP.md           # 领域词汇表索引
```

`bgm-cli/` 是上游参考实现的独立 checkout，不在本仓库版本控制内。

## 已知边界

这个项目是学习/练手作品，不是生产系统。明确没做的：

- **没有 Docker 本地验证** — `docker-compose.yml` 写好了（Postgres + Redis + nginx），但开发机上没装 Docker，一直用 SQLite 直跑，所以 compose 路径**未实测**
- **没有 LLM 生成** — Agent 的工具层接通了，生成层需要 API key，当前留空
- **推荐模块是空壳** — `api/v1/recommend.py` 四个接口只有占位实现
- **测试只有 2 个** — 只覆盖根路径和健康检查
- **`requirements.txt` 里有几项没实际用到** — `pgvector`、`celery`、`redis`、`psycopg2` 都还没接进代码

---

<a id="english"></a>
## English

A full-stack anime catalogue and Q&A platform over [Bangumi.tv](https://bgm.tv) data.

The interesting part is retrieval. Keyword search cannot answer "something that makes you cry" — the word appears in no title, and a `LIKE` query returns zero rows. This project ships **both** a keyword tool and a semantic tool so the difference is visible side by side on the same query.

Subjects are embedded as one chunk each (title, summary, tags, year, studio, episode count). The vector index stores **only `bgm_id` and the embedding**; hits are resolved back against the relational store, which stays the source of truth. See [ADR-0001](docs/adr/0001-retrieval-index-is-a-cache.md).

**Stack:** FastAPI + SQLAlchemy 2.0 + Alembic · React 18 + TypeScript + Vite + Tailwind · LangChain agent with 8 tools · ChromaDB with `jinaai/jina-embeddings-v2-base-zh` (768-dim, local ONNX, no GPU or API key needed).

**Scale:** 41 endpoints across 8 modules, 6 frontend pages, ~5,800 lines of Python and TypeScript, 101 real subjects indexed.

**Note on the embedding model:** ChromaDB's default `all-MiniLM-L6-v2` is English-only and ranks unrelated anime above cyberpunk ones on Chinese queries (`银魂` 0.498 vs `攻壳机动队2.0` 0.246). The project uses a Chinese-native model instead. `BAAI/bge-small-zh-v1.5` was tried first and rejected — its repo ships no ONNX weights.

**Known limits:** this is a learning project. The Docker Compose path is written but never run (no Docker on the dev machine; development used SQLite directly). The agent's tool layer is wired up but generation needs an API key that is currently empty. The recommender endpoints are stubs. Tests cover only two health-check cases.

## License

MIT
