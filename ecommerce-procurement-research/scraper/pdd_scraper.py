from typing import List
from urllib.parse import quote
from .base import BaseScraper, Product


class PddScraper(BaseScraper):
    platform_name = "pdd"
    
    def search_url(self, keyword: str) -> str:
        encoded = quote(keyword)
        return f"https://mobile.pinduoduo.com/search_result.html?search_key={encoded}"
    
    def extract_products(self, page) -> List[Product]:
        products = []
        
        items = page.query_selector_all(".goods-item")
        
        for item in items:
            try:
                name_elem = item.query_selector(".goods-name")
                price_elem = item.query_selector(".price")
                rating_elem = item.query_selector(".rating")
                sales_elem = item.query_selector(".sales")
                link_elem = item.query_selector("a")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem.inner_text().strip()
                
                price_text = price_elem.inner_text().strip().replace("¥", "").replace(",", "")
                price = float(price_text) if price_text else 0.0
                
                rating_text = rating_elem.inner_text().strip() if rating_elem else "0"
                rating = self._parse_rating(rating_text)
                
                sales_text = sales_elem.inner_text().strip() if sales_elem else "0"
                sales = self._parse_sales(sales_text)
                
                url = link_elem.get_attribute("href") if link_elem else ""
                if url and not url.startswith("http"):
                    url = "https://mobile.pinduoduo.com" + url
                
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
    
    def _parse_rating(self, text: str) -> float:
        text = text.replace("评分", "").strip()
        try:
            return float(text)
        except ValueError:
            return 0.0
    
    def _parse_sales(self, text: str) -> int:
        text = text.replace("已拼", "").replace("+", "").replace("万", "0000")
        for char in ["件", " "]:
            text = text.replace(char, "")
        try:
            return int(text)
        except ValueError:
            return 0
