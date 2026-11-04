"""AnimeVault Agent - 动漫知识库问答 Agent"""

import re
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.memory import chat_history_manager
from app.agents.prompts import (
    SYSTEM_PROMPT,
    classify_intent,
    SEARCH_PROMPT,
    RECOMMEND_PROMPT,
    COLLECTION_PROMPT,
    STATS_PROMPT,
    GREETING_PROMPT,
)
from app.agents.tools import (
    search_subjects,
    semantic_search,
    get_subject_detail,
    get_trending_anime,
    get_user_collection,
    update_collection,
    get_user_stats,
    get_calendar,
)
from app.core.config import settings


class AnimeAgent:
    """动漫知识库问答 Agent"""

    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        openai_api_key: str = None,
    ):
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature
        self.api_key = openai_api_key or settings.OPENAI_API_KEY

        if self.api_key:
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                api_key=self.api_key,
                streaming=False,
            )
        else:
            self.llm = None

        self.tools = [
            search_subjects,
            semantic_search,
            get_subject_detail,
            get_trending_anime,
            get_user_collection,
            update_collection,
            get_user_stats,
            get_calendar,
        ]

    def _build_context(
        self,
        user_id: Optional[int],
        session_id: str,
    ) -> str:
        """构建对话上下文信息"""
        context_parts = []

        if user_id:
            context_parts.append(f"当前用户 ID: {user_id}")

            try:
                stats = get_user_stats.invoke({"user_id": user_id})
                context_parts.append(
                    f"用户观看统计: 共 {stats.get('total', 0)} 部番，"
                    f"在看 {stats.get('doing', 0)} 部，"
                    f"看过 {stats.get('collect', 0)} 部"
                )
            except Exception:
                pass

        if context_parts:
            return "\n".join(context_parts)
        return "当前为匿名用户"

    def _generate_response(
        self,
        intent: str,
        message: str,
        tool_results: List[Dict[str, Any]],
        context: str,
    ) -> str:
        """根据意图和工具结果生成最终回答"""

        if not tool_results:
            tool_results_text = "（未调用任何工具）"
        else:
            tool_results_text = "\n\n".join(
                f"【{r.get('tool', 'unknown')} 结果】\n{r.get('result', '')}"
                for r in tool_results
            )

        prompt = f"""
你是一个动漫知识库助手，需要根据以下信息回答用户问题。

## 用户问题
{message}

## 对话上下文
{context}

## 工具调用结果
{tool_results_text}

## 要求
1. 用友好的语气回答
2. 适当使用 emoji
3. 如果工具有返回结果，要基于结果回答
4. 如果工具没有返回结果（如数据库为空），诚实告知用户
5. 推荐时要具体说明推荐理由
6. 不要重复用户的问题
7. 回答要简洁有条理

请直接给出回答：
"""

        if self.llm:
            try:
                response = self.llm.invoke(
                    [
                        SystemMessage(content=SYSTEM_PROMPT),
                        HumanMessage(content=prompt),
                    ]
                )
                return response.content
            except Exception as e:
                return f"抱歉，AI 服务暂时不可用: {str(e)}"

        return self._fallback_response(intent, message, tool_results, context)

    def _fallback_response(
        self,
        intent: str,
        message: str,
        tool_results: List[Dict[str, Any]],
        context: str,
    ) -> str:
        """当没有 OpenAI API Key 时的降级响应"""

        if intent == "greeting":
            return "👋 你好！我是 AnimeVault AI 助手，专门帮你找番、管理追番的！有什么想看的类型吗？"

        if not tool_results:
            return "抱歉，目前数据库为空或 AI 服务未配置。你可以先登录后添加收藏。"

        first_result = tool_results[0].get("result", {})
        results_list = first_result if isinstance(first_result, list) else [first_result]

        if not results_list or (isinstance(results_list[0], dict) and "error" in results_list[0]):
            return "抱歉，搜索结果为空。你可以换个关键词试试，或者告诉我你想看什么类型的番～"

        if intent == "recommend":
            return self._format_recommend_response(results_list)
        elif intent == "search":
            return self._format_search_response(results_list)

        return self._format_generic_response(results_list)

    def _format_recommend_response(self, results: List[Any]) -> str:
        """格式化推荐响应"""
        if not results:
            return "暂无推荐数据"

        lines = ["🎬 为你推荐以下番剧：\n"]
        for i, item in enumerate(results[:5], 1):
            name = item.get("name_cn") or item.get("name", "未知")
            year = item.get("year", "")
            score = item.get("rating_score")
            score_str = f" ⭐ {score}" if score else ""

            lines.append(f"{i}. **{name}** ({year}){score_str}")

        lines.append("\n💡 想了解详情可以说「查看第一个」或「评分多少」")
        return "\n".join(lines)

    def _format_search_response(self, results: List[Any]) -> str:
        """格式化搜索响应"""
        if not results:
            return "没有找到匹配的番剧，试试其他关键词？"

        lines = ["🔍 搜索到以下结果：\n"]
        for i, item in enumerate(results[:5], 1):
            name = item.get("name_cn") or item.get("name", "未知")
            year = item.get("year", "")
            score = item.get("rating_score")
            score_str = f" ⭐ {score}" if score else ""

            lines.append(f"{i}. **{name}** ({year}){score_str}")

        lines.append("\n💡 可以说「查看详情」或「收藏第一个」")
        return "\n".join(lines)

    def _format_generic_response(self, results: List[Any]) -> str:
        """格式化通用响应"""
        if not results:
            return "没有找到相关信息"

        lines = ["📋 查询结果：\n"]
        for item in results[:3]:
            name = item.get("name_cn") or item.get("name", "未知")
            year = item.get("year", "")
            score = item.get("rating_score")
            score_str = f" ⭐ {score}" if score else ""
            lines.append(f"- **{name}** ({year}){score_str}")

        return "\n".join(lines)

    def _parse_collection_command(self, message: str) -> Dict[str, Any]:
        """解析收藏相关命令"""
        result = {}

        status_map = {
            "收藏": "wish",
            "想看": "wish",
            "在看": "doing",
            "追番": "doing",
            "看过": "collect",
            "看完": "collect",
            "完成": "collect",
            "搁置": "on_hold",
            "抛弃": "dropped",
            "弃了": "dropped",
        }

        for keyword, status in status_map.items():
            if keyword in message:
                result["status"] = status
                break

        score_match = re.search(r"(\d+)\s*[分星]", message)
        if score_match:
            score = int(score_match.group(1))
            if 0 <= score <= 10:
                result["rate"] = score

        ep_match = re.search(r"第?\s*(\d+)\s*集", message)
        if ep_match:
            result["ep_status"] = int(ep_match.group(1))

        return result

    async def chat(
        self,
        message: str,
        session_id: str = "default",
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        处理用户对话

        Args:
            message: 用户消息
            session_id: 会话 ID
            user_id: 用户 ID（可选）

        Returns:
            包含回答消息和元数据的字典
        """
        history = chat_history_manager.get_history(session_id)
        history.add_user_message(message)

        intent = classify_intent(message)
        context = self._build_context(user_id, session_id)

        tool_results = []
        tool_calls = []

        if intent == "search":
            keyword = self._extract_keyword(message)
            if keyword:
                try:
                    result = search_subjects.invoke({
                        "keyword": keyword,
                        "subject_type": 2,
                        "limit": 10,
                    })
                    tool_results.append({"tool": "search_subjects", "result": result})
                    tool_calls.append("search_subjects")
                except Exception as e:
                    tool_results.append({"tool": "search_subjects", "result": {"error": str(e)}})

        elif intent == "recommend":
            if "热门" in message or "排行" in message:
                try:
                    result = get_trending_anime.invoke({"limit": 10})
                    tool_results.append({"tool": "get_trending_anime", "result": result})
                    tool_calls.append("get_trending_anime")
                except Exception as e:
                    tool_results.append({"tool": "get_trending_anime", "result": {"error": str(e)}})
            else:
                keyword = self._extract_keyword(message)
                try:
                    result = search_subjects.invoke({
                        "keyword": keyword or self._guess_preference(message),
                        "subject_type": 2,
                        "limit": 10,
                    })
                    tool_results.append({"tool": "search_subjects", "result": result})
                    tool_calls.append("search_subjects")
                except Exception as e:
                    tool_results.append({"tool": "search_subjects", "result": {"error": str(e)}})

        elif intent == "collection":
            if user_id:
                parse_result = self._parse_collection_command(message)
                if parse_result:
                    subject_id = self._extract_subject_id(message)
                    if subject_id:
                        try:
                            result = update_collection.invoke({
                                "user_id": user_id,
                                "subject_id": subject_id,
                                **parse_result,
                            })
                            tool_results.append({"tool": "update_collection", "result": result})
                            tool_calls.append("update_collection")
                        except Exception as e:
                            tool_results.append({"tool": "update_collection", "result": {"error": str(e)}})
                    else:
                        keyword = self._extract_keyword(message) or self._guess_anime_name(message)
                        if keyword:
                            search_result = search_subjects.invoke({
                                "keyword": keyword,
                                "limit": 5,
                            })
                            tool_results.append({"tool": "search_subjects", "result": search_result})
                            tool_calls.append("search_subjects")
                            if search_result and len(search_result) > 0:
                                first_id = search_result[0].get("id")
                                if first_id:
                                    update_result = update_collection.invoke({
                                        "user_id": user_id,
                                        "subject_id": first_id,
                                        **parse_result,
                                    })
                                    tool_results.append({"tool": "update_collection", "result": update_result})
                                    tool_calls.append("update_collection")

        elif intent == "stats" and user_id:
            try:
                result = get_user_stats.invoke({"user_id": user_id})
                tool_results.append({"tool": "get_user_stats", "result": result})
                tool_calls.append("get_user_stats")
            except Exception as e:
                tool_results.append({"tool": "get_user_stats", "result": {"error": str(e)}})

        response_text = self._generate_response(intent, message, tool_results, context)

        history.add_ai_message(response_text)

        return {
            "message": response_text,
            "session_id": session_id,
            "intent": intent,
            "tool_calls": tool_calls,
            "metadata": {
                "user_id": user_id,
                "context": context,
            },
        }

    def _extract_keyword(self, message: str) -> str:
        """从消息中提取搜索关键词"""
        patterns = [
            r"(?:搜索?|找|查|推荐).*?《?(.+?)》?",
            r"《?(.+?)》?",
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                keyword = match.group(1).strip()
                if keyword and len(keyword) >= 2:
                    return keyword

        return message.strip()

    def _extract_subject_id(self, message: str) -> Optional[int]:
        """从消息中提取条目 ID"""
        id_match = re.search(r"id[:：]?\s*(\d+)", message)
        if id_match:
            return int(id_match.group(1))

        num_match = re.search(r"第\s*([一二三四五六七八九十零0-9]+)\s*个", message)
        if num_match:
            num_map = {
                "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
                "零": 0, "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
                "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
            }
            num_str = num_match.group(1)
            return num_map.get(num_str)

        return None

    def _guess_anime_name(self, message: str) -> str:
        """猜测动漫名称"""
        return self._extract_keyword(message)

    def _guess_preference(self, message: str) -> str:
        """猜测用户偏好"""
        preferences = {
            "热血": "热血 战斗",
            "治愈": "治愈 日常",
            "科幻": "科幻 机战",
            "搞笑": "搞笑 喜剧",
            "恋爱": "恋爱 恋爱",
            "校园": "校园 青春",
            "异世界": "异世界 转生",
            "百合": "百合",
            "机战": "机战 机器人",
            "悬疑": "悬疑 推理",
        }

        for pref, keyword in preferences.items():
            if pref in message:
                return keyword

        return ""

