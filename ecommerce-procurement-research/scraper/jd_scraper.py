from typing import List
from urllib.parse import quote
from .base import BaseScraper, Product


class JDScraper(BaseScraper):
    platform_name = "jd"
    
    def search_url(self, keyword: str) -> str:
        encoded = quote(keyword)
        return f"https://search.jd.com/Search?keyword={encoded}"
    
    def extract_products(self, page) -> List[Product]:
        products = []
        
        items = page.query_selector_all(".gl-item")
        
        for item in items:
            try:
                name_elem = item.query_selector(".p-name em")
                price_elem = item.query_selector(".p-price i")
                rating_elem = item.query_selector(".star-rating span")
                sales_elem = item.query_selector(".p-commit a")
                link_elem = item.query_selector(".p-img a")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem.inner_text().strip()
                name = name.replace("\n", "").replace("  ", "")
                
                price_text = price_elem.inner_text().strip() if price_elem else "0"
                price = float(price_text)
                
                rating_text = rating_elem.inner_text().strip() if rating_elem else "0"
                rating = self._parse_rating(rating_text)
                
                sales_text = sales_elem.inner_text().strip() if sales_elem else "0"
                sales = self._parse_sales(sales_text)
                
                url = link_elem.get_attribute("href") if link_elem else ""
                if url and not url.startswith("http"):
                    url = "https://" + url.lstrip("/")
                
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
        text = text.replace("⭐", "").replace("星", "").strip()
        try:
            return float(text)
        except ValueError:
            return 0.0
    
    def _parse_sales(self, text: str) -> int:
        text = text.replace("+", "").replace("万", "0000").replace(".", "")
        for char in ["人", "已", "关", "注", " "]:
            text = text.replace(char, "")
        try:
            return int(text)
        except ValueError:
            return 0
