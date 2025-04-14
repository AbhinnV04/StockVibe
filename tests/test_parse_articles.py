import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup

from scraper_service.parse_articles import parse_articles
from utils.logger import get_logger

logger = get_logger("test_parser_articles")


@pytest.fixture
def mock_soup_valid() -> BeautifulSoup:
    """Fixture to provide a valid mocked BS4 soup object"""
    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="04/10/2025 4:09:13 PM"></time>
        <a class="news-link" href="/article-link">Article Title</a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """
    return BeautifulSoup(html_content, "html.parser")


@pytest.fixture
def mock_soup_invalid_date() -> BeautifulSoup:
    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="invalid-date"></time>
        <a class="news-link" href="/article-link">Article Title</a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """
    return BeautifulSoup(html_content, 'html.parser')


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_valid(mock_logger, mock_soup_valid):
    """Test valid article parsing"""

    result = parse_articles(mock_soup_valid)
    assert len(result) == 1
    assert result[0]['date_time'] == "2025-04-10T16:09:13"
    assert result[0]['source'] == "Business Insider"
    assert result[0]['title'] == "Article Title"
    assert result[0]['link'] == "https://markets.businessinsider.com/article-link"

    mock_logger.warning.assert_not_called()


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_invalid_date(mock_logger, mock_soup_invalid_date):
    """Test invalid date format handling"""

    result = parse_articles(mock_soup_invalid_date)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Invalid or missing date_time, skipping article")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_title(mock_logger):
    """Test missing title handling"""

    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="04/10/2025 4:09:13 PM"></time>
        <a class="news-link" href="/article-link"></a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = parse_articles(soup)

    assert len(result) == 1
    assert result[0]['title'] == "No title"
    mock_logger.warning.assert_any_call(
        "Missing title, using default='No title'")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_link(mock_logger):
    """Test missing article link handling"""

    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="04/10/2025 4:09:13 PM"></time>
        <a class="news-link"></a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = parse_articles(soup)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Missing relative link, skipping article.")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_source(mock_logger):
    """Test missing source handling"""

    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="04/10/2025 4:09:13 PM"></time>
        <a class="news-link" href="/article-link">Article Title</a>
        <span class="latest-news__source"></span>
    </div>
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = parse_articles(soup)

    assert len(result) == 1
    assert result[0]['source'] == "Unknown"
    mock_logger.warning.assert_any_call(
        "Missing Source, using default='Unknown'")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_full_http_link(mock_logger):
    """Test article with full HTTP link handling"""

    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="04/10/2025 4:09:13 PM"></time>
        <a class="news-link" href="https://external.com/news">Article Title</a>
        <span class="latest-news__source">External News</span>
    </div>
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = parse_articles(soup)

    assert len(result) == 1
    assert result[0]['link'] == "https://external.com/news"
    mock_logger.warning.assert_not_called()
