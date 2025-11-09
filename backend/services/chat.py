from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.user import User
from models.chat_message import ChatMessage
from services.db import get_db
from utils.auth_deps import get_current_user

router = APIRouter()


class ChatMessageCreate(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    workspace_id: Optional[int] = None
    visualization_spec: Optional[dict] = None
    interpreter_source: Optional[str] = None


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    workspace_id: Optional[int]
    visualization_spec: Optional[dict]
    interpreter_source: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageOut]
    total: int


@router.post("/messages", response_model=ChatMessageOut)
def create_chat_message(
    message: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a chat message to history"""
    try:
        chat_msg = ChatMessage(
            user_id=user.id,
            workspace_id=message.workspace_id,
            role=message.role,
            content=message.content,
            visualization_spec=message.visualization_spec,
            interpreter_source=message.interpreter_source
        )
        db.add(chat_msg)
        db.commit()
        db.refresh(chat_msg)
        return chat_msg
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


@router.get("/messages", response_model=ChatHistoryResponse)
def get_chat_history(
    workspace_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for current user.

    If workspace_id is provided, returns chat for that workspace only.
    Otherwise returns all user's chat history.
    """
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user.id)

    if workspace_id is not None:
        query = query.filter(ChatMessage.workspace_id == workspace_id)

    total = query.count()
    messages = query.order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()

    return ChatHistoryResponse(messages=messages, total=total)


@router.get("/messages/recent", response_model=List[ChatMessageOut])
def get_recent_messages(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent chat messages for quick access"""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return messages


@router.delete("/messages/{message_id}")
def delete_chat_message(
    message_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific chat message"""
    message = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id, ChatMessage.user_id == user.id)
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        db.delete(message)
        db.commit()
        return {"message": "Chat message deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")


@router.delete("/messages")
def clear_chat_history(
    workspace_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear chat history.

    If workspace_id is provided, clears only that workspace's chat.
    Otherwise clears all user's chat history.
    """
    try:
        query = db.query(ChatMessage).filter(ChatMessage.user_id == user.id)

        if workspace_id is not None:
            query = query.filter(ChatMessage.workspace_id == workspace_id)

        count = query.delete()
        db.commit()

        return {"message": f"Deleted {count} chat messages"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")
