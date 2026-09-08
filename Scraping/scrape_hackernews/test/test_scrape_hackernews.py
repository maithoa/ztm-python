import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import requests
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from scrape import Article, URL, fetch_hacker_news, parse_hacker_news_articles


def article_row(article_id: str, title: str, url: str, score: int | None) -> str:
	score_row = ""
	if score is not None:
		score_row = f'<tr><td><span id="score_{article_id}">{score} points</span></td></tr>'

	return f'''
		<tr class="athing" id="{article_id}">
			<td class="title"><span class="titleline"><a href="{url}">{title}</a></span></td>
		</tr>
		{score_row}
	'''


class TestFetchHackerNews:
	@patch("scrape.requests.get")
	def test_returns_response_text(self, mock_get):
		response = SimpleNamespace(text="<html></html>", raise_for_status=lambda: None)
		mock_get.return_value = response

		assert fetch_hacker_news() == "<html></html>"
		mock_get.assert_called_once_with(URL, timeout=10)

	@patch("scrape.requests.get", side_effect=requests.RequestException("offline"))
	def test_reraises_request_errors(self, mock_get):
		with pytest.raises(requests.RequestException, match="offline"):
			fetch_hacker_news()


class TestParseHackerNewsArticles:
	def test_returns_articles_above_score_threshold(self):
		html = article_row("1", "Popular article", "https://example.com/popular", 201)

		articles = parse_hacker_news_articles(html)

		assert articles == [
			Article(
				id="1",
				title="Popular article",
				url="https://example.com/popular",
				score=201,
			)
		]

	def test_excludes_articles_at_or_below_score_threshold(self):
		html = "".join(
			[
				article_row("1", "Exactly 200", "https://example.com/200", 200),
				article_row("2", "Low score", "https://example.com/low", 199),
			]
		)

		assert parse_hacker_news_articles(html) == []

	def test_excludes_article_without_a_score(self):
		html = article_row("1", "New article", "https://example.com/new", None)

		assert parse_hacker_news_articles(html) == []

	def test_excludes_empty_or_non_numeric_score_text(self):
		html = """
			<tr class="athing" id="1">
				<td class="title"><span class="titleline"><a href="https://example.com/empty">Empty score</a></span></td>
			</tr>
			<tr><td><span id="score_1"></span></td></tr>
			<tr class="athing" id="2">
				<td class="title"><span class="titleline"><a href="https://example.com/text">Text score</a></span></td>
			</tr>
			<tr><td><span id="score_2">unavailable</span></td></tr>
		"""

		assert parse_hacker_news_articles(html) == []

	def test_ignores_rows_without_a_title_link(self):
		html = '<tr class="athing" id="1"><td class="title"></td></tr>'

		assert parse_hacker_news_articles(html) == []
