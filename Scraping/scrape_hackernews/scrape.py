from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass

from logger_config import get_logger

URL = "https://news.ycombinator.com/"

logger = get_logger(__name__)

@dataclass
class Article:
    id: str
    title: str
    url: str | None
    score: int = 0


def truncate_text(value: str | None, width: int) -> str:
    text = value or ""
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."

def fetch_hacker_news() -> str: 
    logger.info("Fetching Hacker News from %s", URL)
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    logger.info("Fetched Hacker News successfully")
    return response.text

def parse_hacker_news_articles(html: str) -> list[Article]:
    soup = BeautifulSoup(html, "html.parser")

    # Get all the tr with tags "athing submission"
    
    title_rows = soup.select('tr.athing', limit=10)

    articles = []

    for row in title_rows: 
        r_id = row.get('id')
        title_line = row.select_one('.titleline a')
        
        if r_id and title_line:
            title = title_line.get_text(strip=True)
            url = title_line.get('href', None)

            #Look for score value based on the row id
            sid = "score_" + r_id
            score = soup.select_one(f'#{sid}')
            score_text = score.get_text().strip() if score else "0 points"
            score_parts = score_text.split()
            score_value = int(score_parts[0]) if score_parts and score_parts[0].isdigit() else 0
            
            # Only take into consideration articles with a score greater than 200
            if score_value > 200:
                article = Article(id=r_id, title=title, url=url, score=score_value)
                articles.append(article)

    logger.info("Parsed %d articles with score greater than 200", len(articles))
    
    return articles


def main():
    try:
        html = fetch_hacker_news()
    except requests.RequestException as error:
        logger.error("Failed to fetch Hacker News: %s", error)
        print(f"Failed to fetch Hacker News: {error}")
        return

    articles = parse_hacker_news_articles(html)
    if not articles:
        logger.info("No articles found with score greater than 200")
        print("No articles found with a score greater than 200.")
        return

    #Print in a table format of 4 columns
    print(f"{'ID':<10} {'Title':<50} {'URL':<50} {'Score':<10}")
    for article in articles:
        title = truncate_text(article.title, 50)
        url = truncate_text(article.url, 50)
        print(f"{article.id:<10} {title:<50} {url:<50} {article.score:<10}")
    logger.info("Printed %d articles", len(articles))


if __name__ == "__main__":
    main()
