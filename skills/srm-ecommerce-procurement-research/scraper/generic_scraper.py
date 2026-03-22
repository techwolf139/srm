import re
from typing import List
from .base import BaseScraper, Product


class GenericScraper(BaseScraper):
    platform_name = "generic"
    
    COMMON_SELECTORS = [
        ".product-item",
        ".item-product",
        ".goods-item",
        ".product-card",
        "[data-product]",
        ".search-result-item",
        ".listing-item",
    ]
    
    NAME_SELECTORS = [
        "h3", ".title", ".product-title", ".item-title",
        ".name", "[class*='title']", "[class*='name']",
    ]
    
    PRICE_SELECTORS = [
        ".price", ".product-price", ".item-price",
        "[class*='price']", "[data-price]",
    ]
    
    RATING_SELECTORS = [
        ".rating", ".stars", ".score",
        "[class*='rating']", "[class*='star']",
    ]
    
    SALES_SELECTORS = [
        ".sales", ".sold", ".deal-count",
        "[class*='sales']", "[class*='sold']",
    ]
    
    def search_url(self, keyword: str) -> str:
        return keyword
    
    def extract_products(self, page) -> List[Product]:
        products = []
        items = self._find_items(page)
        
        for item in items:
            try:
                name = self._extract_name(item)
                price = self._extract_price(item)
                rating = self._extract_rating(item)
                sales = self._extract_sales(item)
                url = self._extract_url(item)
                
                if not name or price <= 0:
                    continue
                
                products.append(Product(
                    name=name,
                    price=price,
                    rating=rating,
                    sales_volume=sales,
                    platform=self.platform_name,
                    source_url=url
                ))
            except Exception:
                continue
        
        return products
    
    def _find_items(self, page) -> List:
        for selector in self.COMMON_SELECTORS:
            items = page.query_selector_all(selector)
            if items:
                return items
        return []
    
    def _extract_name(self, item) -> str:
        for selector in self.NAME_SELECTORS:
            elem = item.query_selector(selector)
            if elem:
                text = elem.inner_text().strip()
                if text:
                    return text
        return ""
    
    def _extract_price(self, item) -> float:
        for selector in self.PRICE_SELECTORS:
            elem = item.query_selector(selector)
            if elem:
                text = elem.inner_text().strip()
                price = self._parse_price(text)
                if price > 0:
                    return price
        return 0.0
    
    def _extract_rating(self, item) -> float:
        for selector in self.RATING_SELECTORS:
            elem = item.query_selector(selector)
            if elem:
                text = elem.inner_text().strip()
                rating = self._parse_rating(text)
                if rating > 0:
                    return rating
        return 0.0
    
    def _extract_sales(self, item) -> int:
        for selector in self.SALES_SELECTORS:
            elem = item.query_selector(selector)
            if elem:
                text = elem.inner_text().strip()
                sales = self._parse_sales(text)
                if sales > 0:
                    return sales
        return 0
    
    def _extract_url(self, item) -> str:
        link = item.query_selector("a")
        if link:
            url = link.get_attribute("href") or ""
            if url and not url.startswith("http"):
                url = "https://" + url.lstrip("/")
            return url
        return ""
    
    def _parse_price(self, text: str) -> float:
        text = re.sub(r"[^\d.,]", "", text)
        text = text.replace(",", "")
        try:
            return float(text)
        except ValueError:
            return 0.0
    
    def _parse_rating(self, text: str) -> float:
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            rating = float(match.group(1))
            return rating if rating <= 5 else rating / 20
        return 0.0
    
    def _parse_sales(self, text: str) -> int:
        text = text.lower()
        text = text.replace("万", "0000").replace("k", "000")
        text = re.sub(r"[^\d]", "", text)
        try:
            return int(text) if text else 0
        except ValueError:
            return 0
