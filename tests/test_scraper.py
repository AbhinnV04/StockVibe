import pytest
from bs4 import BeautifulSoup
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from scraper_service.fetch_html import get_soup


@patch("scraper_service.fetch_html.requests.get")
def test_get_soup_success(mock_get):
    """Test scraper_service.fetch_html.get_soup() with a mock request"""
    # Mock Instance of Get Request
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body><p>Hi there</p></body></html>"
    mock_get.return_value = mock_response

    # Execute mock request
    soup = get_soup("https://example.com")

    # Assess the mock request made
    assert isinstance(soup, BeautifulSoup)
    assert soup.find("p").text == "Hi there" 
    mock_get.assert_called_once()


@patch("scraper_service.fetch_html.requests.get")
def test_get_soup_retries_on_failure(mock_get):
    """Tests the failure of state, exponential backoff decorator"""
    mock_get.side_effect = RequestException("Simulated failure")

    with pytest.raises(Exception, match="Max retries exceeded"):
        get_soup("https://example.com")

    assert mock_get.call_count == 3
