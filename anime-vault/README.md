# AnimeVault

动漫知识库 + 智能问答的全栈应用。数据源 [Bangumi.tv](https://bgm.tv)，后端 FastAPI，前端 React。

> 项目总览、检索效果对比、架构图见 [上级 README](../README.md)。

## 技术栈

- **前端**: React 18 + TypeScript + Vite + TailwindCSS + Zustand + TanStack Query
- **后端**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic
- **Agent**: LangChain，8 个工具
- **检索**: ChromaDB + `jinaai/jina-embeddings-v2-base-zh`（768 维，本地 ONNX 推理）
- **存储**: SQLite（开发默认）/ PostgreSQL（compose 里配了，未实测）

## 快速开始

### 环境要求

只需要 Python 和 Node：

- Python >= 3.11
- Node.js >= 18

默认配置用 SQLite，**不需要装 PostgreSQL 或 Redis**。

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 灌数据 + 建向量索引

```bash
cd backend
python scripts/reindex.py --fetch 100
```

拉取 Bangumi 排行榜 Top 100 存入关系库，并重建向量索引。索引是**可重建的缓存**，随时 `--rebuild`。

如果 `api.bgm.tv` 直连超时，在 `.env` 里设 `BGM_PROXY=http://127.0.0.1:10808`（换成你自己的代理端口）。

### Docker

`docker-compose.yml` 配了 Postgres + Redis + nginx 的完整编排，但**开发机上没装 Docker，这条路径没有实测过**。见 [已知边界](../README.md#已知边界)。

## 目录

```
backend/
├── app/
│   ├── api/v1/       # 8 个路由模块，41 个接口
│   ├── agents/       # LangChain Agent + 8 个工具
│   ├── services/     # 同步、语义检索
│   ├── models/       # SQLAlchemy 模型
│   └── providers/    # Bangumi API 客户端
├── scripts/reindex.py
└── tests/
frontend/src/         # 6 个页面
nginx/
```

## 功能模块

- **动漫知识库** — 条目、剧集、角色、制作人员，从 Bangumi 同步
- **语义检索** — 按含义找番，不是按标题关键词
- **AI 对话** — Agent 编排多个工具回答「有什么让人哭的动画」这类问题
- **追番管理** — 收藏、进度、评分
- **管理接口** — 数据同步、用户管理、统计

## License

MIT
