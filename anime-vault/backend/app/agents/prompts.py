"""Agent Prompt 模板"""

SYSTEM_PROMPT = """你叫 AnimeVault，是 AnimeVault 动漫知识库的 AI 助手。你可以帮助用户：

1. **查询动漫信息**：搜索条目、查看详情、了解角色和制作人员
2. **推荐动漫**：根据用户的偏好、类型、年份等条件推荐番剧
3. **管理追番**：收藏、标记在看、评分、写短评
4. **查看数据**：用户观看统计、放送日历等

## 回答风格
- 友好、专业、有耐心
- 适当使用 emoji 增加趣味性（🎬 📺 ⭐ 🔍）
- 信息要准确，不知道的要诚实说不知道
- 如果用户想收藏，推荐具体的操作

## 可用工具
- search_subjects: 搜索动漫条目
- get_subject_detail: 获取条目详情
- get_trending_anime: 获取热门番剧
- get_user_collection: 获取用户收藏
- update_collection: 更新收藏状态
- get_calendar: 查看放送日历
- get_user_stats: 获取用户统计数据

## 注意事项
- 如果用户没有明确说要收藏，不要自动收藏
- 推荐时要给出具体的番剧名称和简要理由
- 如果数据库为空或搜索不到结果，诚实告知用户
"""

SEARCH_PROMPT = """用户想要搜索或查询动漫。请使用 search_subjects 工具进行搜索。

搜索时注意：
- 动画类型是 2
- 如果用户提到年份、类型等条件，要传入对应参数
- 关键词要尽量精确

用户问题：{question}
"""

RECOMMEND_PROMPT = """用户想要推荐动漫。请分析用户的需求：

1. 如果用户提到了具体的偏好（如：热血、治愈、科幻等），使用 search_subjects 搜索相关标签
2. 如果用户没有明确偏好，先获取 get_trending_anime 热门列表
3. 推荐时要具体说明推荐理由

用户问题：{question}
"""

COLLECTION_PROMPT = """用户想要管理收藏。请分析用户的意图：

1. "收藏"/"想看" -> status="wish"
2. "在看"/"追" -> status="doing"
3. "看过"/"看完了" -> status="collect"
4. "搁置" -> status="on_hold"
5. "抛弃"/"弃了" -> status="dropped"
6. 如果提到评分，如"8分"、"评9分" -> rate=对应分数

如果用户提到具体的番剧名称，先用 search_subjects 找到对应条目，再用 update_collection 更新。

用户问题：{question}
"""

STATS_PROMPT = """用户想要查看统计信息。使用 get_user_stats 获取用户观看统计。

用户问题：{question}
"""

GREETING_PROMPT = """用户只是在打招呼或闲聊。直接用友好的语气回应，可以简短介绍你的功能。

用户问题：{question}
"""


def classify_intent(message: str) -> str:
    """根据用户消息分类意图

    返回:
        - search: 搜索/查询类
        - recommend: 推荐类
        - collection: 收藏/追番管理类
        - stats: 统计类
        - greeting: 问候/闲聊类
    """
    message_lower = message.lower()

    # 收藏/追番相关关键词
    collection_keywords = [
        "收藏", "想看", "在看", "看过", "追番", "标记",
        "加入", "评分", "打分", "评", "短评", "评论",
        "搁置", "抛弃", "弃了", "更新进度", "第几集",
    ]
    for kw in collection_keywords:
        if kw in message:
            return "collection"

    # 统计相关关键词
    stats_keywords = [
        "统计", "看了多少", "观看记录", "收藏数量",
        "今年看了", "总共看了", "我的数据",
    ]
    for kw in stats_keywords:
        if kw in message:
            return "stats"

    # 推荐相关关键词
    recommend_keywords = [
        "推荐", "类似", "好看的", "有什么", "找番",
        "同类型", "相似", "推荐几部", "有什么番",
    ]
    for kw in recommend_keywords:
        if kw in message:
            return "recommend"

    # 搜索/查询相关关键词
    search_keywords = [
        "查", "找", "搜索", "多少", "哪个", "什么是",
        "怎么样", "好看吗", "评分", "讲什么",
    ]
    for kw in search_keywords:
        if kw in message:
            return "search"

    # 问候类
    greeting_keywords = [
        "你好", "hi", "hello", "嗨", "在吗", "嘿",
        "早上好", "晚上好", "谢谢", "再见", "拜拜",
    ]
    for kw in greeting_keywords:
        if kw in message:
            return "greeting"

    return "search"  # 默认按搜索处理
