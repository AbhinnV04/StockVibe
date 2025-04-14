import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup

from scraper_service.parse_articles import parse_articles


@pytest.fixture
def mock_soup() -> BeautifulSoup:
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
def mock_soup_invalid() -> BeautifulSoup:
    """Fixture to provide an invalid mocked BS4 soup object"""
    html_content = """
    <div class="latest-news__story">
        <time class="latest-news__date" datetime="invalid-date"></time>
        <a class="news-link" href="/article-link">Article Title</a>
        <span class="latest-news__source">Business Insider</span>
    </div>
    """
    return BeautifulSoup(html_content, 'html.parser')


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_valid(mock_logger, mock_soup):
    """Test valid article parsing"""

    result = parse_articles(mock_soup)

    assert len(result) == 1
    assert result[0]['date_time'] == "2025-04-10T16:09:13"
    assert result[0]['source'] == "Business Insider"
    assert result[0]['title'] == "Article Title"
    assert result[0]['link'] == "https://markets.businessinsider.com/article-link"

    # Check if any warnings were logged
    mock_logger.warning.assert_not_called()


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_invalid_date(mock_logger, mock_soup_invalid):
    """Test invalid date format handling"""

    result = parse_articles(mock_soup_invalid)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Invalid or missing date_time, skipping article")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_title(mock_logger, mock_soup_invalid):
    """Test missing title handling"""

    # Make title missing
    mock_soup_invalid.find('a', class_="news-link").string = None

    result = parse_articles(mock_soup_invalid)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Missing title, using default='No title'")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_link(mock_logger, mock_soup_invalid):
    """Test missing article link handling"""

    # Make link missing
    mock_soup_invalid.find('a', class_="news-link")['href'] = None

    result = parse_articles(mock_soup_invalid)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Missing article link, skipping article.")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_missing_source(mock_logger, mock_soup_invalid):
    """Test missing source handling"""

    # Make source missing
    mock_soup_invalid.find('span', class_="latest-news__source").string = None

    result = parse_articles(mock_soup_invalid)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Missing Source, using default='Unknown'")


@patch("scraper_service.parse_articles.logger")
def test_parse_articles_invalid_link(mock_logger, mock_soup_invalid):
    """Test malformed link handling"""

    # Make link invalid
    mock_soup_invalid.find('a', class_="news-link")['href'] = "/invalid-link"

    result = parse_articles(mock_soup_invalid)

    assert len(result) == 0
    mock_logger.warning.assert_any_call(
        "Missing article link, skipping article.")
