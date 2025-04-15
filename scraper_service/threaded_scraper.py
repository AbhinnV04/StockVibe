# scraper_service/threaded_scraper.py

from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper_service.fetch_html import get_soup
from scraper_service.parse_articles import parse_articles
from utils.logger import get_logger

logger = get_logger("scraper_service/threaded_scraper.py")


def scraper_single_url(url: str) -> list[dict]:
    """Scrapes a single url / one page"""
    soup = get_soup(url)
    if soup:
       return parse_articles(soup)
    return []

def threaded_scraper(urls: list[str], max_workers: int = 5) -> list[dict]:
    """Thread workers for multiple pages"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(scraper_single_url, url):
                url for url in urls
        }
        
        for future in as_completed(future_to_url):
            try:
                articles = future.result()
                results.extend(articles)
            except Exception as e:
                logger.error(f"Error processing URL {future_to_url[future]}: {e}")
    return results