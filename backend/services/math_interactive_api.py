from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from .math_interactive_service import generate_math_data
from utils.auth_deps import get_current_user
from models.user import User
import logging

router = APIRouter()
logger = logging.getLogger("math_interactive_api")


class MathInteractiveRequest(BaseModel):
    expression: str
    x_range: Optional[Tuple[float, float]] = None
    y_range: Optional[Tuple[float, float]] = None
    include_derivative: bool = False
    include_integral: bool = False
    include_annotations: bool = True
    parameters: Optional[Dict[str, float]] = None


class MathInteractiveResponse(BaseModel):
    function: Dict[str, Any]
    derivative: Optional[Dict[str, Any]] = None
    integral: Optional[Dict[str, Any]] = None
    annotations: Optional[List[Dict[str, Any]]] = None
    parameters: List[str]
    x_range: List[float]
    y_range: List[float]


@router.post("/visualize/math/interactive", response_model=MathInteractiveResponse)
async def visualize_math_interactive(
    request: MathInteractiveRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate interactive mathematical visualization data.
    Returns JSON with function points, derivatives, integrals, and annotations.

    Example request:
    {
        "expression": "x**2 - 4*x + 3",
        "x_range": [-2, 6],
        "include_derivative": true,
        "include_annotations": true
    }

    Example response:
    {
        "function": {
            "points": {"x": [...], "y": [...]},
            "expression": "x**2 - 4*x + 3"
        },
        "derivative": {
            "points": {"x": [...], "y": [...]},
            "expression": "2*x - 4"
        },
        "annotations": [
            {"x": 2.0, "y": -1.0, "label": "local minimum", "type": "min"},
            {"x": 1.0, "y": 0.0, "label": "root", "type": "root"},
            {"x": 3.0, "y": 0.0, "label": "root", "type": "root"},
            {"x": 0.0, "y": 3.0, "label": "y-intercept", "type": "intercept"}
        ],
        "parameters": [],
        "x_range": [-2, 6],
        "y_range": [-10, 10]
    }
    """
    try:
        logger.info(f"Generating interactive math data for expression: {request.expression}")

        result = generate_math_data(
            expression=request.expression,
            x_range=request.x_range,
            y_range=request.y_range,
            include_derivative=request.include_derivative,
            include_integral=request.include_integral,
            include_annotations=request.include_annotations,
            parameters=request.parameters
        )

        return MathInteractiveResponse(**result)

    except ValueError as e:
        logger.error(f"Invalid expression: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating math data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate mathematical data: {str(e)}")
