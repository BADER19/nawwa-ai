import httpx
import logging
from typing import Optional

logger = logging.getLogger("wikipedia_image")


async def fetch_wikipedia_image(person_name: str) -> Optional[str]:
    """
    Fetch the main image URL for a person from Wikipedia.
    Returns the image URL if found, None otherwise.
    """
    try:
        # Step 1: Search Wikipedia for the person
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": person_name,
            "srlimit": 1
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data.get("query", {}).get("search"):
                logger.warning(f"No Wikipedia page found for: {person_name}")
                return None

            page_title = search_data["query"]["search"][0]["title"]
            logger.info(f"Found Wikipedia page: {page_title}")

            # Step 2: Get the page image
            image_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "pageimages",
                "piprop": "original",
                "pilicense": "any"
            }

            image_response = await client.get(search_url, params=image_params)
            image_response.raise_for_status()
            image_data = image_response.json()

            pages = image_data.get("query", {}).get("pages", {})
            if not pages:
                logger.warning(f"No pages data for: {page_title}")
                return None

            # Get the first (and only) page
            page = next(iter(pages.values()))

            if "original" in page:
                image_url = page["original"]["source"]
                logger.info(f"Found Wikipedia image: {image_url}")
                return image_url
            else:
                logger.warning(f"No image found on Wikipedia page: {page_title}")
                return None

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching Wikipedia image for {person_name}: {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error fetching Wikipedia image for {person_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching Wikipedia image for {person_name}: {str(e)}")
        return None


def fetch_wikipedia_image_sync(person_name: str) -> Optional[str]:
    """
    Synchronous version - fetches Wikipedia image for a person.
    """
    try:
        # Step 1: Search Wikipedia for the person
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": person_name,
            "srlimit": 1
        }

        with httpx.Client(timeout=10.0) as client:
            search_response = client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data.get("query", {}).get("search"):
                logger.warning(f"No Wikipedia page found for: {person_name}")
                return None

            page_title = search_data["query"]["search"][0]["title"]
            logger.info(f"Found Wikipedia page: {page_title}")

            # Step 2: Get the page image
            image_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "pageimages",
                "piprop": "original",
                "pilicense": "any"
            }

            image_response = client.get(search_url, params=image_params)
            image_response.raise_for_status()
            image_data = image_response.json()

            pages = image_data.get("query", {}).get("pages", {})
            if not pages:
                logger.warning(f"No pages data for: {page_title}")
                return None

            # Get the first (and only) page
            page = next(iter(pages.values()))

            if "original" in page:
                image_url = page["original"]["source"]
                logger.info(f"Found Wikipedia image: {image_url}")
                return image_url
            else:
                logger.warning(f"No image found on Wikipedia page: {page_title}")
                return None

    except Exception as e:
        logger.error(f"Error fetching Wikipedia image for {person_name}: {str(e)}")
        return None
