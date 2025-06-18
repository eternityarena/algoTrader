from finlight_client import FinlightApi, ApiConfig
from finlight_client.models import GetArticlesParams

def main():
    client = FinlightApi(
        config=ApiConfig(
            api_key="sk_afd107579fb3bc76d6cf497ba121242735b2134091d4d2522f9f056a542b2327"
        )
    )

    params = GetArticlesParams(query="", sources=["www.reuters.com"], from_="2025-05-28", to="2025-05-29", language="en", pageSize=100,page=1)
    articles = client.articles.get_basic_articles(params=params)
    print(articles)

if __name__ == "__main__":
    main()