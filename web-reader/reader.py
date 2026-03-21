"""
Web Reader - Jina Reader API 封装
"""
import os
import requests
from dataclasses import dataclass
from typing import Optional


JINA_API_KEY = os.getenv("JINA_API_KEY", "")


@dataclass
class WebPage:
    url: str
    title: str
    content: str
    timestamp: str


def read_url(url: str, api_key: str = None) -> str:
    """
    使用 Jina Reader 读取网页内容
    
    Args:
        url: 目标 URL
        api_key: Jina API Key（可选）
    
    Returns:
        Markdown 格式的网页内容
    """
    key = api_key or JINA_API_KEY
    
    headers = {}
    if key:
        headers["X-Token"] = key
    
    response = requests.get(
        f"https://r.jina.ai/{url}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch {url}: {response.status_code}")


def read_url_json(url: str, api_key: str = None) -> WebPage:
    """
    使用 Jina Reader 读取网页内容（JSON 格式）
    
    Returns:
        WebPage 对象
    """
    key = api_key or JINA_API_KEY
    
    headers = {
        "Accept": "application/json"
    }
    if key:
        headers["X-Token"] = key
    
    response = requests.get(
        f"https://r.jina.ai/{url}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return WebPage(
            url=data.get("url", url),
            title=data.get("title", ""),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", "")
        )
    else:
        raise Exception(f"Failed to fetch {url}: {response.status_code}")


def read_urls(urls: list[str], api_key: str = None) -> list[str]:
    """
    批量读取多个 URL
    
    Args:
        urls: URL 列表
        api_key: Jina API Key
    
    Returns:
        Markdown 内容列表
    """
    results = []
    for url in urls:
        try:
            content = read_url(url, api_key)
            results.append(content)
        except Exception as e:
            results.append(f"Error reading {url}: {e}")
    return results


if __name__ == "__main__":
    # Demo
    test_url = "https://example.com"
    
    print(f"Reading: {test_url}")
    content = read_url(test_url)
    print(f"Content length: {len(content)} chars")
    print(f"First 200 chars:\n{content[:200]}")
