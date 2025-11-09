import httpx
from fastapi import HTTPException
from fastapi.responses import Response
import logging

logger = logging.getLogger("image_proxy")


async def fetch_external_image(url: str) -> Response:
    """Fetch an external image and return it as a response to avoid CORS issues."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Get content type from the response
            content_type = response.headers.get("content-type", "image/png")

            logger.info(f"Successfully fetched image from {url}, content-type: {content_type}")

            # Return the image with appropriate headers
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                    "Access-Control-Allow-Origin": "*",
                }
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching image from {url}: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch image: {str(e)}")
    except httpx.RequestError as e:
        logger.error(f"Request error fetching image from {url}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching image from {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")
