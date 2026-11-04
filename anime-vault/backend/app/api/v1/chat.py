import json
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.anime_agent import AnimeAgent
from app.agents.memory import chat_history_manager
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["对话"])

# 全局 Agent 实例
agent = AnimeAgent()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """发送消息给 Agent"""
    session_id = req.session_id or f"user_{current_user.id}"

    result = await agent.chat(
        message=req.message,
        session_id=session_id,
        user_id=current_user.id,
    )

    return ChatResponse(
        message=result["message"],
        session_id=result["session_id"],
        metadata={
            "intent": result.get("intent"),
            "tool_calls": result.get("tool_calls"),
        },
    )


@router.post("/stream")
async def send_message_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """流式发送消息给 Agent"""
    session_id = req.session_id or f"user_{current_user.id}"

    async def generate():
        result = await agent.chat(
            message=req.message,
            session_id=session_id,
            user_id=current_user.id,
        )

        full_message = result["message"]
        final_session_id = result["session_id"]

        yield f"data: {json.dumps({'type': 'session_id', 'session_id': final_session_id})}\n\n"

        chunk_size = 3
        for i in range(0, len(full_message), chunk_size):
            chunk = full_message[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            import asyncio
            await asyncio.sleep(0.02)

        if result.get("tool_calls"):
            yield f"data: {json.dumps({'type': 'tool_calls', 'tool_calls': result.get('tool_calls')})}\n\n"

        if result.get("intent"):
            yield f"data: {json.dumps({'type': 'intent', 'intent': result.get('intent')})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取聊天历史"""
    history = chat_history_manager.get_history(session_id)
    messages = [
        {
            "role": msg.type,
            "content": msg.content,
        }
        for msg in history.messages_list
    ]
    return {"session_id": session_id, "messages": messages}


@router.get("/sessions")
def list_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取会话列表"""
    sessions = chat_history_manager.list_sessions(current_user.id)
    return {"sessions": sessions}


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除会话"""
    chat_history_manager.delete_history(session_id)
    return {"message": "会话已删除", "session_id": session_id}
