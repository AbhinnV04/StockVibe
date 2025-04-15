# scraper_service/parse_articles.py

from bs4 import BeautifulSoup
from datetime import datetime
import json

from utils.logger import get_logger

BASE_URL = "https://markets.businessinsider.com"
logger = get_logger("scraper_service/parse_articles.py")


def get_page_range(soup: BeautifulSoup) -> range:
    """Returns the number of pages for a slug"""
    nav = soup.find(
        "nav",
        class_="pagination"
    )
    if not nav:
        return range(1, 2)  # single page

    data_range = nav.get('data-pagination-range')
    if not data_range:
        return range(1, 2)  # single page

    parsed_range = json.loads(data_range.replace("'", '"'))
    range_list = parsed_range.get('range', [1])
    return range(1, range_list[-1] + 1)


def validate_date(date_str) -> str | None:
    """Validate date format MM/DD/YYYY HH:MM:SS AM/PM"""
    try:
        # Try to parse the date with the specific format from the website
        parsed_date = datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
        # Return in ISO 8601 format
        return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def parse_articles(soup: BeautifulSoup) -> list[dict] | list[None]:
    """Parse data from a single article"""
    article_data = []
    articles = soup.find_all(
        "div",
        class_="latest-news__story"
    )
    if not articles:
        logger.warning("No articles found on the page.")
        return []

    for article in articles:
        try:
            # DateTime
            date_time = article.find(
                "time",
                class_="latest-news__date"
            ).get("datetime")
            date_time = validate_date(date_time)
            if not date_time:
                logger.warning(
                    "Invalid or missing date_time, skipping article")
                continue

            # Title
            title = article.find(
                "a",
                class_="news-link"
            ).text.strip()
            if not title or title == "":
                title = "No title"
                logger.warning("Missing title, using default='No title'")

            # Source
            source = article.find(
                "span",
                class_="latest-news__source"
            ).text.strip()
            if not source:
                source = "Unknown"
                logger.warning("Missing Source, using default='Unknown'")

            # Link
            link_tag = article.find("a", class_="news-link")
            if link_tag:
                relative_link = link_tag.get("href")
                if not relative_link:
                    logger.warning("Missing relative link, skipping article.")
                    continue
            else:
                logger.warning("Missing article link, skipping article.")
                continue

            # Construct full link
            if relative_link.startswith("http"):
                full_link = relative_link
            else:
                full_link = BASE_URL + relative_link

            # Append
            article_data.append(
                {
                    "date_time": date_time,
                    "source": source,
                    "title": title,
                    "link": full_link,
                    "top_sentiment": None,
                    "sentiment_score": None
                }
            )

        except AttributeError as e:
            logger.error(f"AttributeError while parsing article: {e}")
        except KeyError as e:
            logger.error(f"KeyError while accessing HTML elements: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while parsing article: {e}")

    return article_data


if __name__ == "__main__":
    from bs4 import BeautifulSoup

    # Sample HTML with various issues to trigger logs
    html = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="invalid-date"></time>
        <a class="news-link" href="/article-link">Article Title</a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """

    soup = BeautifulSoup(html, 'html.parser')
    articles = parse_articles(soup)

    print("\nParsed articles:")
    for a in articles:
        print(a)
