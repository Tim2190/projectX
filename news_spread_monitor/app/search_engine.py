"""Search news and web content via APIs."""

import requests
from typing import List, Optional

SERP_API_URL = "https://serpapi.com/search.json"
GNEWS_API_URL = "https://gnews.io/api/v4/search"
CONTEXTUALWEB_API_URL = (
    "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/WebSearchAPI"
)


def search_serpapi(query: str, api_key: str, num: int = 10) -> List[dict]:
    """Search using SerpApi and return list of results."""
    params = {"q": query, "api_key": api_key, "num": num}
    resp = requests.get(SERP_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("organic_results", [])


def search_gnews(query: str, api_key: str, max_results: int = 10) -> List[dict]:
    """Search news using GNews API."""
    params = {"q": query, "token": api_key, "max": max_results, "lang": "en"}
    resp = requests.get(GNEWS_API_URL, params=params, timeout=10)
    if resp.status_code != 200:
        return []
    data = resp.json()
    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append(
            {
                "title": a.get("title"),
                "link": a.get("url"),
                "snippet": a.get("description", ""),
                "published": a.get("publishedAt"),
            }
        )
    return results


def search_contextualweb(query: str, api_key: str, host: str, num: int = 10) -> List[dict]:
    """Search web using ContextualWeb API."""
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": host}
    params = {"q": query, "pageNumber": 1, "pageSize": num, "autoCorrect": "true"}
    resp = requests.get(
        CONTEXTUALWEB_API_URL, headers=headers, params=params, timeout=10
    )
    if resp.status_code != 200:
        return []
    data = resp.json()
    value = data.get("value", [])
    results = []
    for v in value:
        results.append(
            {
                "title": v.get("title"),
                "link": v.get("url"),
                "snippet": v.get("description", ""),
                "published": v.get("datePublished"),
            }
        )
    return results


def search(
    query: str,
    api_key: str,
    num: int = 10,
    engine: str = "serpapi",
    host: Optional[str] = None,
) -> List[dict]:
    """Search using selected engine."""
    if engine == "gnews":
        return search_gnews(query, api_key, max_results=num)
    if engine == "contextualweb":
        if not host:
            raise ValueError("host required for contextualweb")
        return search_contextualweb(query, api_key, host, num=num)
    return search_serpapi(query, api_key, num=num)
