# scraper_service/fetch_html

import requests
from bs4 import BeautifulSoup

from utils.decorators.retry_with_backoff import retry_with_backoff


@retry_with_backoff(max_retries=3, base_delay=1)
def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")
