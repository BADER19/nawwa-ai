from fastapi import APIRouter, Query
from .image_proxy import fetch_external_image

router = APIRouter()


@router.get("/proxy")
async def proxy_image(url: str = Query(..., description="External image URL to proxy")):
    """Proxy external images to avoid CORS issues."""
    return await fetch_external_image(url)
