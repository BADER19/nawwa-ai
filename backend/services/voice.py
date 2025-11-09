from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from utils.auth_deps import get_current_user
from services.llm_service import interpret_with_source
from services.config import get_tier_config
from services.db import get_db
from services.subscription_service import check_usage_limit, increment_usage
from models.chat_message import ChatMessage
from utils.schema_validators import VisualSpec
from openai import OpenAI
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/voice/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transcribe audio using OpenAI Whisper API and return visualization.

    Flow:
    1. Check if user's tier allows voice input (PRO+)
    2. Transcribe audio with Whisper
    3. Pass transcription to visualization pipeline
    4. Return visualization spec
    """

    # Check tier permissions
    tier_config = get_tier_config(user.subscription_tier.value)
    if not tier_config.get("enable_voice", False):
        raise HTTPException(
            status_code=403,
            detail="Voice input requires PRO tier or higher. Upgrade to unlock voice commands!"
        )

    # Check usage limits
    can_use, error_msg = check_usage_limit(user, db)
    if not can_use:
        raise HTTPException(
            status_code=429,
            detail=error_msg,
            headers={"X-Upgrade-Required": "true"}
        )

    try:
        # Read audio file
        audio_data = await audio.read()

        # Validate file size (max 25MB for Whisper API)
        if len(audio_data) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Audio file too large. Maximum size is 25MB."
            )

        # Validate audio format
        valid_formats = ["flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"]
        file_ext = audio.filename.split(".")[-1].lower() if audio.filename else "webm"
        if file_ext not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid audio format. Supported: {', '.join(valid_formats)}"
            )

        # Transcribe with OpenAI Whisper
        logger.info(f"Transcribing audio for user {user.id}, size: {len(audio_data)} bytes, format: {file_ext}")

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Create temporary file-like object for Whisper API
        from io import BytesIO
        audio_file = BytesIO(audio_data)
        audio_file.name = f"audio.{file_ext}"

        transcript_response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            language="en"  # Force English transcription to prevent language detection errors
        )

        transcription = transcript_response if isinstance(transcript_response, str) else transcript_response.text
        logger.info(f"Transcription result: '{transcription}'")

        if not transcription or len(transcription.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please speak clearly and try again."
            )

        # Pass transcription to visualization pipeline
        user_tier = user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else str(user.subscription_tier)
        spec_dict, source, err = interpret_with_source(
            transcription,
            user_context=None,
            subscription_tier=user_tier
        )

        if source == "error":
            raise HTTPException(status_code=502, detail=f"AI unavailable: {err or 'unknown error'}")

        # Validate spec
        validated = VisualSpec.model_validate(spec_dict)

        # Save chat history - user message (voice transcription)
        user_message = ChatMessage(
            user_id=user.id,
            role="user",
            content=f"🎤 {transcription}"  # Prefix with mic emoji to indicate voice
        )
        db.add(user_message)

        # Save chat history - assistant response
        assistant_message = ChatMessage(
            user_id=user.id,
            role="assistant",
            content=f"Created visualization from voice input using {source}",
            visualization_spec=spec_dict,
            interpreter_source=source
        )
        db.add(assistant_message)

        # Increment usage count
        increment_usage(user, db)

        # Commit
        try:
            db.commit()
            logger.info(f"Saved voice visualization for user {user.id}, usage: {user.usage_count}")
        except Exception as e:
            logger.error(f"Failed to save voice chat/usage: {e}")
            db.rollback()

        return {
            "transcription": transcription,
            "visualization": validated.model_dump(),
            "source": source,
            "usage_count": user.usage_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process voice input: {str(e)}"
        )
