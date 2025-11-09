from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from utils.schema_validators import VisualizeRequest, VisualSpec
from utils.auth_deps import get_current_user
from services.llm_service import interpret_command, interpret_with_source
from services.config import AI_REQUIRE
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
from services.db import get_db
from services.subscription_service import check_usage_limit, increment_usage
from models.chat_message import ChatMessage


router = APIRouter()


@router.post("/", response_model=VisualSpec)
def visualize(
    req: VisualizeRequest,
    response: Response,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if len(req.command) > 2000:
        raise HTTPException(status_code=400, detail="Command too long (max 2000 characters)")

    # Check usage limits based on subscription tier
    can_use, error_msg = check_usage_limit(user, db)
    if not can_use:
        raise HTTPException(
            status_code=429,
            detail=error_msg,
            headers={"X-Upgrade-Required": "true"}
        )

    # If quota was reset, commit that change before proceeding
    if user.usage_count == 0 and datetime.utcnow() >= user.usage_reset_date - timedelta(seconds=60):
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Failed to commit quota reset: {e}")
            db.rollback()

    # Pass user's subscription tier to LLM service for tier-based model selection
    user_tier = user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else str(user.subscription_tier)
    spec_dict, source, err = interpret_with_source(req.command, user_context=req.user_context, subscription_tier=user_tier)
    print(f"[VISUALIZE] spec_dict before validation: {spec_dict.keys()}")
    print(f"[VISUALIZE] nodes in spec_dict: {'nodes' in spec_dict}")
    print(f"[VISUALIZE] links in spec_dict: {'links' in spec_dict}")
    if 'nodes' in spec_dict:
        print(f"[VISUALIZE] nodes value: {spec_dict['nodes'][:2] if spec_dict['nodes'] else None}")
    # Expose interpreter source in a response header for debugging
    response.headers["X-Interpreter-Source"] = source
    if source == "error" or (AI_REQUIRE and source == "fallback"):
        raise HTTPException(status_code=502, detail=f"AI unavailable: {err or 'unknown error'}")
    validated = VisualSpec.model_validate(spec_dict)
    print(f"[VISUALIZE] After validation - nodes: {validated.nodes}")
    print(f"[VISUALIZE] After validation - links: {validated.links}")
    print(f"[VISUALIZE] After validation - plotlySpec: {validated.plotlySpec}")
    print(f"[VISUALIZE] Validated dict: {validated.model_dump()}")

    # Save chat history - user message
    user_message = ChatMessage(
        user_id=user.id,
        role="user",
        content=req.command
    )
    db.add(user_message)

    # Save chat history - assistant response
    assistant_message = ChatMessage(
        user_id=user.id,
        role="assistant",
        content=f"Created visualization using {source}",
        visualization_spec=spec_dict,
        interpreter_source=source
    )
    db.add(assistant_message)

    # Increment usage count after successful visualization
    increment_usage(user, db)
    response.headers["X-Usage-Count"] = str(user.usage_count)

    # Commit usage count and chat messages atomically
    try:
        db.commit()
        logger.info(f"Saved visualization for user {user.id}, usage: {user.usage_count}")
    except Exception as e:
        logger.error(f"Failed to save chat/usage: {e}")
        db.rollback()  # Don't fail visualization if save fails, but log the error

    return validated
