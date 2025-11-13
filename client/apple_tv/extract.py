import re
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from client.apple_tv.attributes import Attributes, parse_attributes
from utils.parsing import parse_html
from utils.requests_utils import get_request


def get_apple_tv_artworks(
    url: str,
) -> tuple[Attributes | None, str | None, str | None, str | None]:
    response = get_request(url)
    if response is None:
        return None, None, None, None

    parsed_page = parse_html(response.text)

    attributes = parse_attributes(parsed_page)
    if attributes is None:
        return None, None, None, None

    poster_url = get_poster_url(attributes)
    background_url = get_background_url(parsed_page)
    logo_url = get_logo_url(parsed_page)

    return attributes, poster_url, background_url, logo_url


def get_attributes(url: str) -> Attributes | None:
    response = get_request(url)
    if response is None:
        return None

    parsed_page = parse_html(response.text)
    return parse_attributes(parsed_page)


def get_poster_url(attributes: Attributes) -> str | None:
    if "image" not in attributes:
        return None

    image_url = attributes["image"]
    return get_enlarged_image_url(image_url, "2000x0w.jpg")


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


def get_enlarged_image_url(url: str, target_size: str) -> str:
    """Get the largest available image by replacing size with target_size'2000x0w.jpg'"""

    parts = urlsplit(url)

    # Split path at the last '/'
    path_parts = parts.path.rsplit("/", 1)
    if len(path_parts) == 2:
        path_parts[-1] = target_size
        new_path = "/".join(path_parts)
    else:
        new_path = target_size

    # Rebuild URL with new path
    return urlunsplit(
        (parts.scheme, parts.netloc, new_path, parts.query, parts.fragment)
    )


def get_resized_image_url(url: str, size: str) -> str:
    """Example: size = 3840x2160.jpg"""
    extension = size.split(".")[-1]
    return re.sub(r"[\w]+x[\w]+\-?[\d]+\.{}$".format(extension), size, url)
