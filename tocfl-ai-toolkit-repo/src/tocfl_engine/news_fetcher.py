from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from .utils import load_json, normalize_whitespace


@dataclass
class NewsArticle:
    title: str
    url: str
    summary: str
    content: str
    source: str
    published: str | None = None


class NewsFetcher:
    def __init__(self, data_dir: Path, timeout: int = 20) -> None:
        self.timeout = timeout
        self.config = load_json(data_dir / 'news_sources.json')

    def fetch_articles(self, query: str, limit: int = 5) -> list[NewsArticle]:
        results: list[NewsArticle] = []
        lowered = query.lower()
        for source in self.config.get('rss_sources', []):
            try:
                rss_xml = requests.get(source['rss_url'], timeout=self.timeout).text
                results.extend(self._parse_rss(source['name'], rss_xml, lowered))
            except Exception:
                continue
            if len(results) >= limit:
                break
        final: list[NewsArticle] = []
        for item in results:
            try:
                content = self.fetch_article_content(item.url)
            except Exception:
                content = item.summary
            final.append(NewsArticle(
                title=item.title,
                url=item.url,
                summary=item.summary,
                content=content,
                source=item.source,
                published=item.published,
            ))
            if len(final) >= limit:
                break
        return final

    def _parse_rss(self, source_name: str, xml_text: str, query: str) -> Iterable[NewsArticle]:
        root = ET.fromstring(xml_text)
        items = root.findall('.//item')
        for item in items:
            title = (item.findtext('title') or '').strip()
            link = (item.findtext('link') or '').strip()
            summary = normalize_whitespace(BeautifulSoup(item.findtext('description') or '', 'html.parser').get_text(' '))
            pub_date = item.findtext('pubDate')
            haystack = f"{title} {summary}".lower()
            if query and query not in haystack:
                continue
            if link:
                yield NewsArticle(title=title, url=link, summary=summary, content=summary, source=source_name, published=pub_date)

    def fetch_article_content(self, url: str) -> str:
        html = requests.get(url, timeout=self.timeout, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(html, 'html.parser')
        selectors = ['article', '.article', '.post-content', '.story', 'main']
        text = ''
        for selector in selectors:
            node = soup.select_one(selector)
            if node:
                text = node.get_text(' ', strip=True)
                if len(text) > 120:
                    break
        if not text:
            text = soup.get_text(' ', strip=True)
        text = normalize_whitespace(text)
        text = re.sub(r'更多新聞.*$', '', text)
        return text
