import requests
from bs4 import BeautifulSoup
import pandas as pd
import json 
import os

# BASE_URL = "https://markets.businessinsider.com"
# STOCK_PATH = "/news/nvda-stock"

def getRange(soup) -> range:
    nav = soup.find('nav', class_='pagination')
    data_range = nav.get('data-pagination-range')
    parsed_range = json.loads(data_range.replace("'", '"'))
    range_list = parsed_range.get('range')
    return range(1, (range_list[-1]+1))


columns = ["dateTime", "source", "title", "link", "top_sentiment", "sentiment_score"]
df = pd.DataFrame(columns=columns)

counter = 0

url = "https://markets.businessinsider.com/news/nvda-stock?p=1"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")
pageRange = getRange(soup)

for page in pageRange:
    url = f"https://markets.businessinsider.com/news/nvda-stock?p={page}"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    articles = soup.find_all("div", class_ = "latest-news__story")
    
    for article in articles:
        dateTimeArticle = article.find("time", class_ = "latest-news__date").get("datetime")
        titleArticle = article.find("a", class_ = "news-link").text 
        sourceArticle = article.find("span", class_ = "latest-news__source").text
        linkArticle = article.find("a", class_ = "news-link").get("href")
        
        df = pd.concat([pd.DataFrame([[dateTimeArticle, sourceArticle, titleArticle, linkArticle, None, None]], columns=columns), df], ignore_index=True)
        counter += 1
    
df.to_csv("./articles/nvidia.csv")
print(f"{counter} articles found and scraped")
print(df.head())