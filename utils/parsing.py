from bs4 import BeautifulSoup


def parse_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")
