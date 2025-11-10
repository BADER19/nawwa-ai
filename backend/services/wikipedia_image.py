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

        headers = {
            "User-Agent": "NawwaVisualizationApp/1.0 (https://nawwa.ai; contact@nawwa.ai) httpx/0.24"
        }

        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
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

        headers = {
            "User-Agent": "NawwaVisualizationApp/1.0 (https://nawwa.ai; contact@nawwa.ai) httpx/0.24"
        }

        with httpx.Client(timeout=10.0, headers=headers) as client:
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

            # Fallback: Try to get images from the page content
            logger.info(f"No featured image, trying to fetch images from page content...")
            images_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "images",
                "imlimit": 10
            }

            images_response = client.get(search_url, params=images_params)
            images_response.raise_for_status()
            images_data = images_response.json()

            pages_with_images = images_data.get("query", {}).get("pages", {})
            if pages_with_images:
                page_with_images = next(iter(pages_with_images.values()))
                images_list = page_with_images.get("images", [])

                # Filter for actual image files (not icons/logos)
                for img in images_list:
                    img_title = img.get("title", "")
                    # Skip common non-content images
                    if any(skip in img_title.lower() for skip in ["commons-logo", "icon", "logo.svg", "book-new", "shackle"]):
                        continue

                    # This looks like a real image, get its URL
                    logger.info(f"Found image file: {img_title}")

                    # Get the actual image URL
                    imageinfo_params = {
                        "action": "query",
                        "format": "json",
                        "titles": img_title,
                        "prop": "imageinfo",
                        "iiprop": "url",
                        "iiurlwidth": 800
                    }

                    imageinfo_response = client.get(search_url, params=imageinfo_params)
                    imageinfo_response.raise_for_status()
                    imageinfo_data = imageinfo_response.json()

                    imageinfo_pages = imageinfo_data.get("query", {}).get("pages", {})
                    if imageinfo_pages:
                        imageinfo_page = next(iter(imageinfo_pages.values()))
                        imageinfo = imageinfo_page.get("imageinfo", [])
                        if imageinfo and len(imageinfo) > 0:
                            image_url = imageinfo[0].get("url") or imageinfo[0].get("thumburl")
                            if image_url:
                                logger.info(f"Found Wikipedia content image: {image_url}")
                                return image_url

            logger.warning(f"No image found on Wikipedia page: {page_title}")
            return None

    except Exception as e:
        logger.error(f"Error fetching Wikipedia image for {person_name}: {str(e)}")
        return None
