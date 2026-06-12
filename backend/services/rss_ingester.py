import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import httpx
from backend.config import GRAPH_DATA_DIR

RSS_FEEDS_FILE = Path(GRAPH_DATA_DIR) / "rss_feeds.json"


def _load_feeds() -> list[dict]:
    if RSS_FEEDS_FILE.exists():
        return json.loads(RSS_FEEDS_FILE.read_text())
    return []


def _save_feeds(feeds: list[dict]):
    RSS_FEEDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RSS_FEEDS_FILE.write_text(json.dumps(feeds, indent=2, default=str))


def add_feed(url: str, name: str = "", category: str = "general") -> dict:
    feeds = _load_feeds()
    feed = {
        "id": f"feed_{len(feeds)+1}",
        "url": url,
        "name": name or url,
        "category": category,
        "added_at": datetime.now().isoformat(),
        "last_fetched": None,
        "article_count": 0,
    }
    feeds.append(feed)
    _save_feeds(feeds)
    return feed


def remove_feed(feed_id: str) -> bool:
    feeds = _load_feeds()
    before = len(feeds)
    feeds = [f for f in feeds if f["id"] != feed_id]
    _save_feeds(feeds)
    return len(feeds) < before


def list_feeds() -> list[dict]:
    return _load_feeds()


def fetch_feed(url: str) -> list[dict]:
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)

    articles = []

    # RSS 2.0
    for item in root.iter("item"):
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        desc = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")
        articles.append({
            "title": title,
            "url": link,
            "content": desc,
            "published": pub_date,
            "source": url,
        })

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", "", ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        content_el = entry.find("atom:content", ns) or entry.find("atom:summary", ns)
        content = content_el.text if content_el is not None and content_el.text else ""
        published = entry.findtext("atom:published", "", ns) or entry.findtext("atom:updated", "", ns)
        articles.append({
            "title": title,
            "url": link,
            "content": content,
            "published": published,
            "source": url,
        })

    return articles


def fetch_and_ingest(feed_id: str) -> dict:
    feeds = _load_feeds()
    feed = next((f for f in feeds if f["id"] == feed_id), None)
    if not feed:
        return {"error": "Feed not found"}

    articles = fetch_feed(feed["url"])

    feed["last_fetched"] = datetime.now().isoformat()
    feed["article_count"] = feed.get("article_count", 0) + len(articles)
    _save_feeds(feeds)

    return {
        "feed_id": feed_id,
        "feed_name": feed["name"],
        "articles_fetched": len(articles),
        "articles": articles[:20],
    }
