# AnimeVault — 动漫知识库 Agent 平台

## 一、项目定位

AnimeVault 是一个基于 **Python + FastAPI + React** 的全栈动漫知识库 Agent 服务平台，深度整合 Bangumi.tv 数据源，提供智能问答、个性化推荐、追番管理、数据分析等功能。

### 1.1 项目愿景

打造一个以 **Agent 为核心**的动漫知识中枢，让用户通过自然语言对话即可完成动漫检索、追番管理、个性化推荐等操作，同时提供丰富的可视化数据分析能力。

### 1.2 核心价值

- **智能交互**：自然语言对话替代繁琐的筛选操作
- **数据聚合**：整合 Bangumi 全量数据（条目、角色、人物、剧集）
- **个性化**：基于用户行为的精准推荐
- **可扩展**：模块化设计，支持多数据源接入

### 1.3 目标用户

- 动漫爱好者（追番、找番）
- 数据控（统计分析、榜单）
- 开发者（API 服务、Agent 集成）

---

## 二、技术栈选型

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18+ | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 5.x | 构建工具 |
| TailwindCSS | 3.x | 样式框架 |
| Zustand | 4.x | 状态管理 |
| React Query | 5.x | 数据请求缓存 |
| React Router | 6.x | 路由管理 |
| shadcn/ui | - | UI 组件库 |
| Lucide React | - | 图标库 |
| Recharts | 2.x | 数据可视化 |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12 | 运行时 |
| FastAPI | 0.110+ | Web 框架 |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | 数据库迁移 |
| Pydantic | 2.x | 数据校验 |
| Uvicorn | - | ASGI 服务器 |
| Pytest | 8.x | 测试框架 |

### 2.3 AI / Agent 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| LangChain | 0.2.x | Agent 框架 |
| LangGraph | 0.1.x | 工作流编排 |
| OpenAI API | GPT-4o | 大语言模型 |
| pgvector | - | 向量检索 |
| FAISS | - | 向量索引（备选） |

### 2.4 数据源

| 数据源 | 说明 |
|--------|------|
| **Bangumi P1 API | 主数据源（条目、剧集、角色、人物、收藏） |
| **Bangumi SearchEncore | 增强搜索（社区维护） |
| **自建缓存层 | Redis 缓存热点数据 |

### 2.5 存储

| 存储 | 版本 | 用途 |
|------|------|------|
| PostgreSQL | 16+ | 主数据库 |
| pgvector | - | 向量扩展 |
| Redis | 7.x | 缓存、会话、会话队列 |
| SQLite | - | 开发环境 |

### 2.6 部署与运维

| 技术 | 用途 |
|------|------|
| Docker Compose | 本地开发与部署 |
| Nginx | 反向代理 |
| GitHub Actions | CI/CD |
| Celery + Redis | 异步任务队列 |
| Flower | 任务监控 |

---

## 三、核心功能模块

### 3.1 动漫知识库（Knowledge Base）

#### 3.1.1 数据采集层

**数据实体：

- **条目（Subject）**：动画、漫画、音乐、游戏、小说
- **剧集（Episode）**：正片、SP、OP/ED、预告等
- **角色（Character）**：角色信息、声优、角色收藏
- **人物（Person）**：声优、导演、编剧等制作人员
- **目录（Index）**：用户创建的番剧目录
- **标签（Tag）**：分类标签系统

#### 3.1.2 同步策略

| 策略 | 说明 | 频率 |
|------|------|------|
| 全量同步 | 首次初始化全量数据 | 首次部署 |
| 增量同步 | 按排名/热度分页拉取更新 | 每日 |
| 实时同步 | 热门条目实时更新 | 按需 |
| 用户数据同步 | 用户收藏、评分同步 | 登录时 |

#### 3.1.3 数据质量

- 去重与合并（多数据源）
- 数据完整性校验
- 评分数据归一化
- 标签体系建设

### 3.2 Agent 智能问答（Chat Agent）

#### 3.2.1 对话能力

| 能力 | 示例 |
|------|------|
| **信息查询** | "《进击的巨人》评分多少？" |
| **条件检索** | "推荐几部 2024 年冬季的高分科幻动画" |
| **推荐** | "根据我看过的番推荐类似的" |
| **收藏操作** | "把《咒术回战》加入在看" |
| **进度更新** | "我看完了《葬送的芙莉莲》第 12 集" |
| **数据分析** | "我今年看了多少部番？" |
| **闲聊** | "今天有什么新番更新？" |

#### 3.2.2 多轮对话

- 上下文记忆（会话历史
- 上下文窗口管理
- 会话持久化

### 3.3 个性化推荐引擎

#### 3.3.1 推荐策略

| 策略 | 算法 | 说明 |
|------|------|------|
| 基于内容 | 标签相似度 | 基于标签、类型、制作公司 |
| 协同过滤 | 用户-based | 相似用户推荐 |
| 混合推荐 | 加权融合 | 多策略融合排序 |
| 热门推荐 | 热度排名 | 排行榜、趋势 |
| 实时推荐 | 行为序列 | 基于最近行为 |

#### 3.3.2 推荐场景

- 首页推荐（千人千面
- 相似条目推荐
- 看过还看过
- 导演/声优作品推荐
- 季节性新番推荐

### 3.4 追番管理（Collection）

#### 3.4.1 收藏状态

| 状态 | 说明 |
|------|------|
| wish | 想看 |
| collect | 收藏（已看过 |
| doing | 在看 |
| on_hold | 搁置 |
| dropped | 抛弃 |

#### 3.4.2 核心功能

- 收藏/取消收藏
- 状态变更
- 评分（0-10 分）
- 短评
- 自定义标签
- 观看进度（集数/卷数）
- 私密收藏
- 批量操作

#### 3.4.3 Bangumi 同步

- 双向同步（AnimeVault ↔ Bangumi）
- OAuth 授权
- 冲突解决策略
- 同步历史记录

### 3.5 管理后台

#### 3.5.1 数据源管理

- 手动导入条目
- 批量同步任务
- 同步日志查看
- 数据质量监控

#### 3.5.2 用户管理

- 用户列表
- 权限管理
- 行为统计

#### 3.5.3 数据统计

- 收录数量统计
- 用户活跃度
- API 调用统计
- Agent 对话统计

---

## 四、数据库设计

### 4.1 核心表结构

#### 4.1.1 条目表（anime_subjects

```sql
CREATE TABLE anime_subjects (
    id SERIAL PRIMARY KEY,
    bgm_id INT UNIQUE NOT NULL,          -- Bangumi 条目 ID
    name VARCHAR(500) NOT NULL,         -- 日文标题
    name_cn VARCHAR(500),              -- 中文标题
    name_en VARCHAR(500),              -- 英文标题
    summary TEXT,                     -- 简介
    subject_type SMALLINT NOT NULL,      -- 类型: 1=书籍 2=动画 3=音乐 4=游戏 6=三次元
    platform VARCHAR(100),              -- 平台
    total_episodes INT DEFAULT 0,       -- 总集数
    status VARCHAR(20),               -- 状态: aired/airing/upcoming
    air_date DATE,                     -- 放送开始日期
    end_date DATE,                     -- 放送结束日期
    season VARCHAR(20),               -- 季度: spring/summer/autumn/winter
    year INT,                          -- 年份
    rating_score DECIMAL(4,2),         -- 评分
    rating_rank INT,                   -- 排名
    rating_total INT,                  -- 评分人数
    popularity_rank INT,                   -- 人气排名
    collect_count INT DEFAULT 0,        -- 收藏人数
    doing_count INT DEFAULT 0,          -- 在看人数
    wish_count INT DEFAULT 0,         -- 想看人数
    collect_user_count INT DEFAULT 0,     -- 看过人数
    on_hold_count INT DEFAULT 0,      -- 搁置人数
    dropped_count INT DEFAULT 0,       -- 抛弃人数
    image JSONB,                         -- 封面图 {large, common, medium, small, grid}
    infobox JSONB,                    -- 信息框数据
    tags JSONB,                       -- 标签列表 [{name, count}]
    genres JSONB,                     -- 分类
    studios JSONB,                    -- 制作公司
    relations JSONB,                  -- 关联条目
    url VARCHAR(1000),                  -- Bangumi 链接
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    synced_at TIMESTAMPTZ             -- 最后同步时间
);

CREATE INDEX idx_subjects_type_status ON anime_subjects(subject_type, status);
CREATE INDEX idx_subjects_year_season ON anime_subjects(year, season);
CREATE INDEX idx_subjects_rating_rank ON anime_subjects(rating_rank);
CREATE INDEX idx_subjects_name_cn_trgm ON anime_subjects USING gin (name_cn gin_trgm_ops);
CREATE INDEX idx_subjects_tags ON anime_subjects USING gin(tags);
```

#### 4.1.2 剧集表（anime_episodes）

```sql
CREATE TABLE anime_episodes (
    id SERIAL PRIMARY KEY,
    bgm_id INT UNIQUE NOT NULL,      -- Bangumi 剧集 ID
    subject_id INT REFERENCES anime_subjects(id) ON DELETE CASCADE,
    name VARCHAR(500),               -- 日文标题
    name_cn VARCHAR(500),            -- 中文标题
    ep INT,                          -- 集数序号
    sort INT,                        -- 排序
    episode_type SMALLINT,            -- 类型: 0=本篇 1=SP 2=OP 3=ED 4=预告 5=MAD 6=其它
    duration VARCHAR(100),                -- 时长
    airdate DATE,                    -- 放送日期
    comment INT DEFAULT 0,               -- 评论数
    desc TEXT,                       -- 简介
    disc INT DEFAULT 0,              -- 碟片序号
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_episodes_subject_id ON anime_episodes(subject_id);
CREATE INDEX idx_episodes_type_sort ON anime_episodes(subject_id, episode_type, sort);
```

#### 4.1.3 角色表（anime_characters）

```sql
CREATE TABLE anime_characters (
    id SERIAL PRIMARY KEY,
    bgm_id INT UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_cn VARCHAR(200),
    role VARCHAR(50),                 -- 角色类型: 主角/配角/客串
    image JSONB,
    infobox JSONB,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_characters_name_cn_trgm ON anime_characters USING gin (name_cn gin_trgm_ops);
```

#### 4.1.4 人物表（anime_persons）

```sql
CREATE TABLE anime_persons (
    id SERIAL PRIMARY KEY,
    bgm_id INT UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_cn VARCHAR(200),
    type SMALLINT,                     -- 类型: 1=个人 2=组合 3=公司
    career JSONB,                    -- 职业: 声优/导演/编剧...
    image JSONB,
    infobox JSONB,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_persons_name_cn_trgm ON anime_persons USING gin (name_cn gin_trgm_ops);
```

#### 4.1.5 条目-角色关联表（anime_subject_characters）

```sql
CREATE TABLE anime_subject_characters (
    id SERIAL PRIMARY KEY,
    subject_id INT REFERENCES anime_subjects(id) ON DELETE CASCADE,
    character_id INT REFERENCES anime_characters(id) ON DELETE CASCADE,
    role VARCHAR(50),
    order_index INT DEFAULT 0,
    UNIQUE(subject_id, character_id)
);

CREATE INDEX idx_subject_char_subject ON anime_subject_characters(subject_id);
CREATE INDEX idx_subject_char_character ON anime_subject_characters(character_id);
```

#### 4.1.6 条目-人物关联表（anime_subject_persons）

```sql
CREATE TABLE anime_subject_persons (
    id SERIAL PRIMARY KEY,
    subject_id INT REFERENCES anime_subjects(id) ON DELETE CASCADE,
    person_id INT REFERENCES anime_persons(id) ON DELETE CASCADE,
    position VARCHAR(100),           -- 职位: 导演/编剧/声优...
    order_index INT DEFAULT 0,
    UNIQUE(subject_id, person_id, position)
);

CREATE INDEX idx_subject_person_subject ON anime_subject_persons(subject_id);
CREATE INDEX idx_subject_person_person ON anime_subject_persons(person_id);
```

#### 4.1.7 用户表（users）

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hashed_password TEXT,
    avatar_url TEXT,
    bio TEXT,
    bgm_user_id INT UNIQUE,            -- Bangumi 用户 ID
    bgm_username VARCHAR(50),           -- Bangumi 用户名
    bgm_access_token TEXT,              -- Bangumi Access Token
    bgm_refresh_token TEXT,           -- Bangumi Refresh Token
    bgm_token_expires_at TIMESTAMPTZ, -- Token 过期时间
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_bgm_id ON users(bgm_user_id);
```

#### 4.1.8 用户收藏表（user_collections）

```sql
CREATE TABLE user_collections (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    subject_id INT REFERENCES anime_subjects(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,    -- wish/collect/doing/on_hold/dropped
    rate SMALLINT CHECK (rate BETWEEN 0 AND 10),
    ep_status INT DEFAULT 0,       -- 看过集数
    vol_status INT DEFAULT 0,      -- 看过卷数
    tags TEXT[] DEFAULT '{}',       -- 自定义标签
    comment TEXT,                  -- 短评
    private BOOLEAN DEFAULT FALSE, -- 私密收藏
    bgm_updated_at TIMESTAMPTZ,     -- Bangumi 更新时间
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, subject_id)
);

CREATE INDEX idx_collections_user_status ON user_collections(user_id, status);
CREATE INDEX idx_collections_subject_id ON user_collections(subject_id);
```

#### 4.1.9 对话记录表（chat_messages）

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL,    -- 会话 ID
    role VARCHAR(20) NOT NULL,          -- user/assistant/system
    content TEXT NOT NULL,
    metadata JSONB,                     -- 引用的条目 ID、工具调用等
    tokens_used INT DEFAULT 0,           -- Token 用量
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_user_session ON chat_messages(user_id, session_id);
CREATE INDEX idx_chat_created_at ON chat_messages(created_at DESC);
```

#### 4.1.10 向量表（anime_embeddings）

```sql
CREATE TABLE anime_embeddings (
    id SERIAL PRIMARY KEY,
    subject_id INT REFERENCES anime_subjects(id) ON DELETE CASCADE,
    embedding vector(1536),            -- OpenAI text-embedding-3-small
    content_type VARCHAR(50),            -- summary/tags/full
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subject_id, content_type)
);

CREATE INDEX idx_embeddings_vector ON anime_embeddings USING hnsw (embedding vector_cosine_ops);
```

#### 4.1.11 同步任务表（sync_tasks）

```sql
CREATE TABLE sync_tasks (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,   -- full/incremental/subject/character/person
    status VARCHAR(20) NOT NULL,     -- pending/running/completed/failed
    total_items INT DEFAULT 0,
    processed_items INT DEFAULT 0,
    failed_items INT DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 五、后端架构设计

### 5.1 分层架构

```
┌─────────────────────────────────────────┐
│           API Layer (FastAPI Routers)        │
├─────────────────────────────────────────┤
│           Service Layer                │
│  (业务逻辑层)                      │
├─────────────────────────────────────────┤
│           Agent Layer                │
│  (LangChain / LangGraph)              │
├─────────────────────────────────────────┤
│           Data Access Layer          │
│  (SQLAlchemy Models / Repositories)     │
├─────────────────────────────────────────┤
│           External APIs                  │
│  (Bangumi API / Redis / Vector DB)    │
└─────────────────────────────────────────┘
```

### 5.2 API 设计

#### 5.2.1 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册 |
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET  | `/api/v1/auth/me` | 当前用户信息 |
| GET  | `/api/v1/auth/bgm/login` | Bangumi OAuth 登录 |
| GET  | `/api/v1/auth/bgm/callback` | Bangumi OAuth 回调 |

#### 5.2.2 条目 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/anime` | 条目列表 |
| GET | `/api/v1/anime/:id` | 条目详情 |
| GET | `/api/v1/anime/:id/episodes` | 剧集列表 |
| GET | `/api/v1/anime/:id/characters` | 角色列表 |
| GET | `/api/v1/anime/:id/persons` | 制作人员 |
| GET | `/api/v1/anime/:id/relations` | 关联条目 |
| GET | `/api/v1/anime/trending` | 热门趋势 |
| GET | `/api/v1/anime/calendar` | 每日放送表 |

#### 5.2.3 搜索 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/search/subjects` | 搜索条目 |
| POST | `/api/v1/search/characters` | 搜索角色 |
| POST | `/api/v1/search/persons` | 搜索人物 |
| GET | `/api/v1/search/suggest` | 搜索建议 |

#### 5.2.4 推荐 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/recommend/personal` | 个性化推荐 |
| GET | `/api/v1/recommend/similar/:id` | 相似推荐 |
| GET | `/api/v1/recommend/season` | 季度新番推荐 |
| GET | `/api/v1/recommend/popular` | 热门推荐 |

#### 5.2.5 收藏 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/collections` | 我的收藏列表 |
| GET | `/api/v1/collections/:subject_id` | 收藏详情 |
| PUT | `/api/v1/collections/:subject_id` | 添加/更新收藏 |
| DELETE | `/api/v1/collections/:subject_id` | 删除收藏 |
| PATCH | `/api/v1/collections/:subject_id/progress` | 更新进度 |
| POST | `/api/v1/collections/sync` | 同步 Bangumi 收藏 |

#### 5.2.6 Chat API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/chat/send` | 发送消息 |
| GET | `/api/v1/chat/sessions` | 会话列表 |
| GET | `/api/v1/chat/sessions/:id` | 会话详情 |
| DELETE | `/api/v1/chat/sessions/:id` | 删除会话 |

#### 5.2.7 管理后台 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/stats` | 统计数据 |
| POST | `/api/v1/admin/sync/trigger` | 触发同步任务 |
| GET | `/api/v1/admin/sync/tasks` | 同步任务列表 |
| GET | `/api/v1/admin/users` | 用户列表 |

---

## 六、Agent 工作流设计

### 6.1 整体架构

```
用户提问
  ↓
对话历史 + 用户信息
  ↓
意图识别 (Intent Classification)
  ↓
工具选择 (Tool Selection)
  ├─ 🔍 search_subjects    → 条目搜索
  ├─ 📖 get_subject    → 条目详情
  ├─ 🎬 list_episodes   → 剧集列表
  ├─ 👤 search_characters → 角色搜索
  ├─ 🎭 search_persons   → 人物搜索
  ├─ 🌟 recommend        → 个性化推荐
  ├─ 📚 get_collection  → 获取收藏
  ├─ ✏️ update_collection → 更新收藏
  ├─ 📅 calendar       → 放送表
  └─ 📊 user_stats      → 用户统计
  ↓
工具执行 (Tool Execution)
  ↓
结果整理 (Response Generation)
  ↓
自然语言回答 + 结构化数据
```

### 6.2 意图分类

| 意图 | 触发关键词 | 工具 |
|------|----------|------|
| 查询类 | "查询"、"找"、"搜索"、"什么是" | search_subjects, get_subject |
| 推荐类 | "推荐"、"类似"、"好看的" | recommend |
| 收藏类 | "收藏"、"想看"、"在看"、"看过" | collection_tools |
| 进度类 | "看到"、"第几集"、"更新进度" | update_collection |
| 角色类 | "角色"、"声优"、"谁配的" | search_characters, search_persons |
| 日程类 | "今天"、"这周"、"更新表" | calendar |
| 统计类 | "统计"、"多少部"、"数据分析" | user_stats |
| 闲聊类 | - | 直接 LLM 回答 |

### 6.3 RAG 实现方案

#### 6.3.1 向量检索流程

1. **向量化**：将条目简介 + 标签拼接后向量化
2. **检索**：pgvector 相似度检索 Top-K
3. **重排序**：结合评分、热度等权重重排序
4. **注入**：检索结果注入 Prompt

#### 6.3.2 多轮对话记忆

- 滑动窗口：最近 N 条消息
- 摘要总结：历史对话摘要
- 实体提取：提取关键实体（条目名、角色名等）

### 6.4 Prompt 设计

#### 6.4.1 System Prompt

```
你是 AnimeVault，一个专业的动漫知识库助手。
你可以帮助用户：
1. 查询动漫信息（评分、简介、角色、制作人员等）
2. 推荐动漫（根据偏好、类型、年份等）
3. 管理追番（收藏、进度、评分）
4. 查看放送日程

回答风格：
- 友好、专业、有帮助
- 提供准确的信息
- 适当使用 emoji 增加可读性
- 如果是动漫爱好者的语气
```

### 6.5 工具定义

#### 6.5.1 search_subjects

```python
@tool
def search_subjects(
    keyword: str,
    subject_type: str = "anime",
    limit: int = 10,
    sort: str = "match"
) -> list:
    """搜索动漫条目"""
    ...
```

#### 6.5.2 get_subject_detail

```python
@tool
def get_subject_detail(subject_id: int) -> dict:
    """获取条目详细信息"""
    ...
```

#### 6.5.3 recommend_anime

```python
@tool
def recommend_anime(
    user_id: int,
    reason: str = "",
    limit: int = 10
) -> list:
    """推荐动漫"""
    ...
```

---

## 七、推荐算法设计

### 7.1 基于内容的推荐

```
相似度 = 标签相似度 × 0.4 + 类型相似度 × 0.2
       + 制作公司相似度 × 0.2 + 评分相似度 × 0.2
```

### 7.2 协同过滤

- 用户-based CF：找到相似用户的收藏
- 物品-based CF：基于用户-物品交互矩阵

### 7.3 混合推荐

```
最终得分 = 内容分 × 0.3 + CF分 × 0.4 + 热度分 × 0.3
```

---

## 八、项目结构

```
anime-vault/
├── frontend/                     # React 前端
│   ├── src/
│   │   ├── components/           # UI 组件
│   │   │   ├── ui/               # 基础组件
│   │   │   ├── anime/            # 动漫相关组件
│   │   │   ├── chat/             # 对话组件
│   │   │   └── layout/           # 布局组件
│   │   ├── pages/                 # 页面路由
│   │   │   ├── home/             # 首页
│   │   │   ├── anime/            # 动漫详情
│   │   │   ├── search/            # 搜索页
│   │   │   ├── collection/       # 收藏页
│   │   │   ├── chat/              # 对话页
│   │   │   └── admin/            # 管理后台
│   │   ├── stores/                # Zustand 状态管理
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   └── collection.ts
│   │   ├── services/              # API 客户端
│   │   │   ├── api.ts
│   │   │   ├── anime.ts
│   │   │   └── chat.ts
│   │   ├── hooks/                 # 自定义 Hooks
│   │   ├── types/                 # TypeScript 类型定义
│   │   ├── utils/                 # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                       # Python 后端
│   ├── app/
│   │   ├── api/                  # FastAPI 路由
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py        # 认证
│   │   │   │   ├── anime.py       # 动漫 CRUD
│   │   │   │   ├── search.py      # 搜索
│   │   │   │   ├── recommend.py   # 推荐
│   │   │   │   ├── collection.py  # 收藏
│   │   │   │   ├── chat.py         # 对话
│   │   │   │   └── admin.py       # 管理后台
│   │   │   └── deps.py           # 依赖注入
│   │   ├── core/                  # 核心配置
│   │   │   ├── config.py         # 环境变量配置
│   │   │   ├── security.py      # JWT/密码
│   │   │   └── database.py     # DB 连接
│   │   ├── models/                # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── anime.py          # 动漫模型
│   │   │   ├── user.py           # 用户模型
│   │   │   ├── collection.py     # 收藏模型
│   │   │   └── chat.py           # 对话模型
│   │   ├── schemas/               # Pydantic 校验
│   │   │   ├── anime.py
│   │   │   ├── user.py
│   │   │   ├── collection.py
│   │   │   └── chat.py
│   │   ├── services/              # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── anime_service.py      # 动漫服务
│   │   │   ├── search_service.py   # 搜索服务
│   │   │   ├── recommend_service.py# 推荐服务
│   │   │   ├── collection_service.py # 收藏服务
│   │   │   ├── sync_service.py     # 同步服务
│   │   │   └── stats_service.py    # 统计服务
│   │   ├── agents/                # LangChain Agent
│   │   │   ├── __init__.py
│   │   │   ├── anime_agent.py     # 动漫问答 Agent
│   │   │   ├── tools.py            # Agent 工具集
│   │   │   ├── prompts.py          # Prompt 模板
│   │   │   └── memory.py           # 对话记忆
│   │   ├── providers/             # 外部服务
│   │   │   ├── __init__.py
│   │   │   ├── bangumi.py           # Bangumi API 客户端
│   │   │   └── openai.py          # OpenAI 客户端
│   │   ├── tasks/                 # Celery 任务
│   │   │   ├── __init__.py
│   │   │   ├── sync_tasks.py       # 同步任务
│   │   │   └── worker.py           # Worker 配置
│   │   ├── repositories/          # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── anime_repo.py
│   │   │   └── user_repo.py
│   │   └── utils/                 # 工具函数
│   │       ├── __init__.py
│   │       └── exceptions.py
│   ├── alembic/                   # 数据库迁移
│   ├── tests/                     # 测试
│   │   ├── api/
│   │   ├── services/
│   │   ├── agents/
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── main.py
│
├── docker-compose.yml           # 一键启动
├── nginx/                        # Nginx 配置
│   └── default.conf
├── .env.example
└── README.md
```

---

## 九、部署方案

### 9.1 Docker Compose 服务

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: animevault
      POSTGRES_USER: animevault
      POSTGRES_PASSWORD: animevault
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://animevault:animevault@postgres:5432/animevault
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend

  celery_worker:
    build: ./backend
    command: celery -A app.tasks.worker worker --loglevel=info
    depends_on:
      - postgres
      - redis

  celery_beat:
    build: ./backend
    command: celery -A app.tasks.worker beat --loglevel=info
    depends_on:
      - postgres
      - redis
```

### 9.2 环境变量

```env
# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/animevault

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# Bangumi
BGM_APP_ID=your-app-id
BGM_APP_SECRET=your-app-secret
BGM_REDIRECT_URI=http://localhost:3000/auth/bgm/callback

# 同步配置
SYNC_CONCURRENCY=8
SYNC_RATE_LIMIT=100/min
```

---

## 十、开发路线图

### Phase 1: MVP（2 周）基础功能

- [ ] 项目脚手架搭建
- [ ] 数据库设计与迁移
- [ ] Bangumi API 客户端
- [ ] 条目数据同步
- [ ] 基础 CRUD API
- [ ] 前端基础页面

### Phase 2:（2 周）收藏与搜索

- [ ] 用户认证（JWT + Bangumi OAuth）
- [ ] 收藏管理
- [ ] 全文搜索
- [ ] 前端收藏页
- [ ] 搜索页

### Phase 3:（3 周）Agent 对话

- [ ] LangChain 集成
- [ ] 工具集开发
- [ ] RAG 向量检索
- [ ] 对话前端
- [ ] 对话历史

### Phase 4:（2 周）推荐系统

- [ ] 基于内容推荐
- [ ] 协同过滤
- [ ] 混合推荐
- [ ] 推荐页前端

### Phase 5:（2 周）管理后台 & 优化

- [ ] 管理后台
- [ ] 数据统计
- [ ] 性能优化
- [ ] 部署文档

---

## 十一、简历亮点

| 维度 | 体现的能力 |
|------|-----------|
| **全栈开发** | React 18 + TypeScript + FastAPI + PostgreSQL + Redis |
| **AI/Agent** | LangChain + LangGraph + RAG + Function Calling + pgvector |
| **工程能力** | Docker 容器化 + CI/CD + Alembic 迁移 + Celery 异步任务 |
| **数据工程** | 多数据源聚合 + 定时同步 + 缓存策略 + 数据质量监控 |
| **算法** | 协同过滤推荐 + 内容推荐 + 混合推荐 + 全文检索 |
| **API 设计** | RESTful API + WebSocket + OAuth2.0 + 版本化 API |
| **系统设计** | 分层架构 + 微服务思想 + 高可用 + 可扩展 |

---

## 十二、与现有 bgm-cli 的关系

AnimeVault 与 [bgm-cli](file:///d:/bangumi/bgm-cli/README.md) 项目的关系：

### 12.1 互补关系

- **bgm-cli**：命令行工具，面向开发者/重度用户
- **AnimeVault**：Web 平台，面向普通用户

### 12.2 可复用资源

| 资源 | 说明 |
|------|------|
| Bangumi API 封装逻辑 | API 调用方式、数据结构理解 |
| 数据模型设计 | 条目/剧集/角色/人物模型 |
| 收藏状态语义 | wish/collect/doing/on_hold/dropped |
| 搜索过滤逻辑 | 类型/标签/评分/排名 |

### 12.3 未来整合方向

- bgm-cli 可作为 AnimeVault 的 CLI 客户端
- 共享数据同步逻辑
- 共享 Agent 工具集
