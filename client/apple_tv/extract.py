import re

from bs4 import BeautifulSoup
from utils.parsing import parse_html
from utils.requests_utils import get_request


def get_apple_tv_artworks(url: str) -> tuple[str | None, str | None]:
    response = get_request(url)
    if response is None:
        return None, None

    parsed_page = parse_html(response.text)

    logo_url = get_logo_url(parsed_page)
    background_url = get_background_url(parsed_page)

    return background_url, logo_url


def get_logo_url(page: BeautifulSoup) -> str | None:
    """Logo is first picture with class starting with "picture" """
    pattern = re.compile(r"^picture")
    pictures = page.find_all("picture", class_=pattern)

    if not pictures:
        return None

    return get_image_url(pictures[0], "2400x900", "png")


def get_background_url(page: BeautifulSoup) -> str | None:
    """Background is first picture with class starting with "svelte" """
    pattern = re.compile(r"^svelte")
    pictures = page.find_all("picture", class_=pattern)

    if not pictures:
        return None

    return get_image_url(pictures[0], "4320x3240", "jpg")


def get_image_url(picture: BeautifulSoup, size: str, extension: str) -> str | None:
    srcsets = [source.get("srcset") for source in picture.find_all("source")]
    srcset = None
    file_extension = f".{extension} "
    for srcset in srcsets:
        if file_extension in srcset:
            break
    if not srcset:
        return None

    image_url = srcset.split(", ")[0].split(" ")[0]
    target_size = f"{size}.{extension}"
    return get_resized_image_url(image_url, target_size)


def get_resized_image_url(url: str, size: str) -> str:
    """Example: size = 3840x2160.jpg"""
    extension = size.split(".")[-1]
    return re.sub(r"[\w]+x[\w]+\-?[\d]+\.{}$".format(extension), size, url)
