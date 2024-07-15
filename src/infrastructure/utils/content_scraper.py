import os
from src.infrastructure.utils.content_helper import Helper
from newsapi import NewsApiClient

class Scraper:
    def __init__(self, newsapi_cred_path):
        newsapi_key = Helper.load_json(newsapi_cred_path)["api_key"]
        self.newsapi = NewsApiClient(api_key=newsapi_key)

    def get_latest_news(self, keyword):
        print(self.newsapi.get_everything(keyword, sort_by="relevancy", language="en")["articles"][0]["content"])
        # for article in self.newsapi.get_everything(keyword, sort_by="relevancy", language="en")["articles"]:
        #     print(article["content"])
