import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

BASE_URL = "https://markets.businessinsider.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_page_range(soup: BeautifulSoup) -> range:
    nav = soup.find('nav', class_='pagination')
    if not nav:
        return range(1, 2)

    data_range = nav.get('data-pagination-range')
    if not data_range:
        return range(1, 2)

    parsed_range = json.loads(data_range.replace("'", '"'))
    range_list = parsed_range.get('range', [1])
    return range(1, range_list[-1] + 1)


def parse_articles(soup: BeautifulSoup) -> list:
    articles_data = []
    articles = soup.find_all("div", class_="latest-news__story")

    for article in articles:
        try:
            date_time = article.find("time", class_="latest-news__date").get("datetime")
            title = article.find("a", class_="news-link").text.strip()
            source = article.find("span", class_="latest-news__source").text.strip()
            relative_link = article.find("a", class_="news-link").get("href")
            full_link = relative_link if relative_link.startswith("http") else BASE_URL + relative_link

            articles_data.append([date_time, source, title, full_link, None, None])
        except Exception as e:
            print(f"Error parsing article: {e}")
            continue

    return articles_data


def scrape_stock_news(stock_slug: str) -> pd.DataFrame:
    """Scrapes news articles for a given stock slug (e.g., 'nvda-stock', 'tata_motors_5-stock')"""
    columns = ["dateTime", "source", "title", "link", "top_sentiment", "sentiment_score"]
    df = pd.DataFrame(columns=columns)

    stock_url = f"{BASE_URL}/news/{stock_slug}"
    soup = get_soup(stock_url)
    page_range = get_page_range(soup)

    for page in page_range:
        print(f"Scraping {stock_slug} - Page {page}")
        url = f"{stock_url}?p={page}"
        soup = get_soup(url)
        articles = parse_articles(soup)
        df = pd.concat([df, pd.DataFrame(articles, columns=columns)], ignore_index=True)

    return df


def save_dataframe(df: pd.DataFrame, stock_slug: str):
    filename = stock_slug.replace("/", "_")
    path = f"./articles/{filename}.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} articles to {path}")


if __name__ == "__main__":
    # EXAMPLES:
    stock_slug = "nvda-stock"              # NVIDIA
    # stock_slug = "tata_motors_5-stock"   # Tata Motors

    df = scrape_stock_news(stock_slug)
    save_dataframe(df, stock_slug)
    print(df.head())
