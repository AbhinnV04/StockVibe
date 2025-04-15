import pytest
from unittest.mock import patch
from bs4 import BeautifulSoup
import json

from scraper_service.parse_articles import get_page_range
from utils.logger import get_logger

logger = get_logger("test_parser_articles.page_range")


def test_get_page_range_valid():
    html = """
    <nav class='pagination' data-pagination-range="{'range':[1,2,3,4,5]}"></nav>
    """
    soup = BeautifulSoup(html, 'html.parser')
    result = get_page_range(soup)
    assert list(result) == [1, 2, 3, 4, 5]

def test_get_page_range_missing_nav():
    html = "<html><body><div>No pagination</div></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    result = get_page_range(soup)
    assert list(result) == [1]

def test_get_page_range_missing_data():
    html = "<nav class='pagination'></nav>"
    soup = BeautifulSoup(html, 'html.parser')
    result = get_page_range(soup)
    assert list(result) == [1]
