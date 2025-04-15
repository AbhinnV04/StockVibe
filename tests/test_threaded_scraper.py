# tests/test_threaded_scraper.py

import pytest 
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from scraper_service.threaded_scraper import threaded_scraper


@patch("scraper_service.threaded_scraper.parse_articles")
@patch("scraper_service.threaded_scraper.get_soup")
def test_threaded_scraper(mock_fetch_html, mock_parse_articles):
    """Test threaded scraper with mock inputs"""
    
    mock_soup = BeautifulSoup("<div></div>", "html.parser")
    mock_fetch_html.return_value = mock_soup
    mock_parse_articles.return_value = [
        {
            "title": "Article A",
            "link": "url",
            "date_time": "2025-04-10T10:00:00", 
            "source": "BI", 
            "top_sentiment": None, 
            "sentiment_score": None
        }
    ]
    
    urls = ["http://example.com/page1", "http://example.com/page2"]
    
    results = threaded_scraper(urls=urls, max_workers=2)
    
    assert mock_fetch_html.call_count == len(urls)
    assert mock_parse_articles.call_count == len(urls)
    assert len(results) == len(urls)
    assert results[0]["title"] == "Article A"
    
    
@patch("scraper_service.threaded_scraper.parse_articles")
@patch("scraper_service.threaded_scraper.scraper_single_url") 
def test_threaded_scraper_fetch_error(mock_fetch_html, mock_parse_articles):
    mock_fetch_html.side_effect = [Exception("Network error"), BeautifulSoup("<div></div>", "html.parser")]
    mock_parse_articles.return_value = [{"title": "B", "link": "url", "date_time": "now", "source": "X", "top_sentiment": None, "sentiment_score": None}]
    
    urls = ["bad-url", "good-url"]
    results = threaded_scraper(urls)

    assert len(results) == 1

    