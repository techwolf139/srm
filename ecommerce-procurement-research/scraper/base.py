"""
Abstract base class for e-commerce scrapers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse


@dataclass
class Product:
    name: str
    price: float
    rating: float
    sales_volume: int
    platform: str
    source_url: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "rating": self.rating,
            "sales_volume": self.sales_volume,
            "platform": self.platform,
            "source_url": self.source_url,
        }


class BaseScraper(ABC):
    platform_name: str = "base"
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
    
    @abstractmethod
    def search_url(self, keyword: str) -> str:
        pass
    
    @abstractmethod
    def extract_products(self, page) -> List[Product]:
        pass
    
    def detect_platform(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        platform_map = {
            "taobao.com": "taobao",
            "tmall.com": "taobao",
            "jd.com": "jd",
            "pdd.com": "pdd",
            "1688.com": "1688",
            "amazon.com": "amazon",
            "amazon.co.uk": "amazon",
        }
        
        for domain_pattern, platform in platform_map.items():
            if domain_pattern in domain:
                return platform
        return None
    
    def close(self):
        if self.browser:
            self.browser.close()
