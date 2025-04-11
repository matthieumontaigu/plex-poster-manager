import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


def get_request(url: str, params: dict = {}) -> requests.Response | None:
    """
    Make a GET request to the specified URL with retry logic.
    """
    session = requests.Session()

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.3 Safari/605.1.15"
        )
    }
    try:
        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f"{e}")
        return None
