# AnimeVault — 动漫知识库 Agent 平台

基于 **Python + FastAPI + React** 的全栈动漫知识库 Agent 服务平台，深度整合 Bangumi.tv 数据源，提供智能问答、个性化推荐、追番管理等功能。

## 技术栈

- **前端**: React 18 + TypeScript + Vite + TailwindCSS + Zustand
- **后端**: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **AI/Agent**: LangChain + LangGraph + OpenAI API + pgvector
- **存储**: PostgreSQL + Redis
- **部署**: Docker Compose

## 快速开始

### 环境要求

- Python >= 3.12
- Node.js >= 20
- PostgreSQL >= 16 (with pgvector)
- Redis >= 7

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### Docker 一键启动

```bash
docker-compose up -d
```

## 项目结构

```
anime-vault/
├── frontend/          # React 前端
├── backend/           # FastAPI 后端
├── nginx/             # Nginx 配置
├── docker-compose.yml
└── README.md
```

## 功能模块

- 📚 **动漫知识库**: 多数据源聚合，全量条目同步
- 🤖 **Agent 智能问答**: RAG 检索增强，自然语言对话
- 🎯 **个性化推荐**: 协同过滤 + 内容推荐
- 📺 **追番管理**: 收藏、进度、评分、标签
- 🛠️ **管理后台**: 数据同步、用户管理、统计分析

## License

MIT
