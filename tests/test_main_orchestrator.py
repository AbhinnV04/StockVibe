from unittest.mock import patch, MagicMock
import pandas as pd
from main import main

@patch("main.threaded_scraper")
@patch("main.get_page_range")
@patch("main.get_soup")
def test_main_flow(mock_soup, mock_page_range, mock_scraper):
    mock_soup.return_value = MagicMock()
    mock_page_range.return_value = range(1,3)
    mock_scraper.return_value = [
        {
            "title": "Fake Title",
            "link": "http://example.com",
            "date_time": "2025-04-10T10:00:00",
            "source": "MockSource",
            "top_sentiment": None,
            "sentiment_score": None
        }
    ]

    main("https://example.com", "mock-stock")

    df = pd.read_csv("logs/mock-stock_output.csv")
    assert not df.empty
    assert df.iloc[0]["title"] == "Fake Title"
