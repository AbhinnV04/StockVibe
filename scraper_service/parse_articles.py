# scraper_service/parse_articles.py

from bs4 import BeautifulSoup
from datetime import datetime

from utils.logger import get_logger

BASE_URL = "https://markets.businessinsider.com"
logger = get_logger("scraper_service/parse_articles.py")


def validate_date(date_str) -> str | None:
    """Validate date format MM/DD/YYYY HH:MM:SS AM/PM"""
    try:
        # Try to parse the date with the specific format from the website
        parsed_date = datetime.strptime(date_str, "%m/%d/%Y %I:%M:%S %p")
        return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")  # Return in ISO 8601 format
    except ValueError:
        return None 

def parse_articles(soup: BeautifulSoup) -> list:
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
            if not title:
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
