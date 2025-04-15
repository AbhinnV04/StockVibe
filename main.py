import pandas as pd

from scraper_service.fetch_html import get_soup
from scraper_service.parse_articles import get_page_range
from scraper_service.threaded_scraper import threaded_scraper
from utils.logger import get_logger

logger = get_logger("main.py")
BASE_URL = "https://markets.businessinsider.com"


def main(url: str, slug: str) -> None:
    """Main orchestrator for StockVibe scraping and saving pipeline"""

    logger.info("Starting StockVibe scraper...")

    try:
        soup = get_soup(url)
        total_pages = get_page_range(soup)

        logger.info(f"Found {total_pages} pages for {slug}")

        urls = [f"{url}?p={i}" for i in total_pages]

        results = threaded_scraper(urls)
        results_df = pd.DataFrame(results)

        filename_slug = slug.replace("/", "_")
        output_path = f"logs/{filename_slug}_output.csv"
        results_df.to_csv(output_path, index=False)

        logger.info(f"Scraped data saved to {output_path}")
    except Exception as e:
        logger.error(f"Unexpected Exception during process: {e}")


if __name__ == "__main__":
    test_slug = "nvda-stock"
    test_url = f"{BASE_URL}/news/{test_slug}"
    main(test_url, test_slug)
