"""对话记忆管理"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory


class InMemoryChatHistory(BaseChatMessageHistory):
    """内存中的对话历史"""

    def __init__(self, session_id: str, max_messages: int = 20):
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: List[BaseMessage] = []

    def add_user_message(self, message: str) -> None:
        self.messages.append(HumanMessage(content=message))
        self._trim_history()

    def add_ai_message(self, message: str) -> None:
        self.messages.append(AIMessage(content=message))
        self._trim_history()

    def _trim_history(self) -> None:
        """保留最近的消息，移除旧消息"""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def clear(self) -> None:
        self.messages = []

    @property
    def messages_list(self) -> List[BaseMessage]:
        return self.messages


class ChatHistoryManager:
    """对话历史管理器"""

    def __init__(self):
        self._histories: Dict[str, InMemoryChatHistory] = {}

    def get_history(self, session_id: str) -> InMemoryChatHistory:
        if session_id not in self._histories:
            self._histories[session_id] = InMemoryChatHistory(session_id)
        return self._histories[session_id]

    def delete_history(self, session_id: str) -> None:
        if session_id in self._histories:
            del self._histories[session_id]

    def list_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """列出用户的所有会话"""
        result = []
        for session_id, history in self._histories.items():
            if history.messages:
                last_msg = history.messages[-1]
                result.append(
                    {
                        "session_id": session_id,
                        "last_message": last_msg.content[:100],
                        "last_time": datetime.now().isoformat(),
                        "message_count": len(history.messages),
                    }
                )
        return result


# 全局单例
chat_history_manager = ChatHistoryManager()
