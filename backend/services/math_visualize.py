from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from .math_plot_service import generate_math_plot
from utils.auth_deps import get_current_user
from models.user import User
import logging

router = APIRouter()
logger = logging.getLogger("math_visualize")


class MathVisualizeRequest(BaseModel):
    elements: List[Dict[str, Any]]


class MathVisualizeResponse(BaseModel):
    imageUrl: str


@router.post("/visualize/math", response_model=MathVisualizeResponse)
async def visualize_math(
    request: MathVisualizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a mathematical plot from element specifications.
    Returns a base64-encoded PNG image.
    """
    try:
        logger.info(f"Generating math plot for user {current_user.id} with {len(request.elements)} elements")

        if not request.elements:
            raise HTTPException(status_code=400, detail="No elements provided")

        # Generate plot
        image_url = generate_math_plot(request.elements)

        return MathVisualizeResponse(imageUrl=image_url)

    except Exception as e:
        logger.error(f"Error generating math plot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate mathematical plot: {str(e)}")
