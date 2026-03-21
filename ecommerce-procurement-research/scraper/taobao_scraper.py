from typing import List
from urllib.parse import quote
from .base import BaseScraper, Product


class TaobaoScraper(BaseScraper):
    platform_name = "taobao"
    
    def search_url(self, keyword: str) -> str:
        encoded = quote(keyword)
        return f"https://s.taobao.com/search?q={encoded}"
    
    def extract_products(self, page) -> List[Product]:
        products = []
        
        items = page.query_selector_all(".item")
        
        for item in items:
            try:
                name_elem = item.query_selector(".title")
                price_elem = item.query_selector(".price")
                rating_elem = item.query_selector(".star")
                sales_elem = item.query_selector(".deal-cnt")
                link_elem = item.query_selector("a")
                
                if not name_elem or not price_elem:
                    continue
                
                name = name_elem.inner_text().strip()
                price_text = price_elem.inner_text().strip().replace("¥", "").replace(",", "")
                price = float(price_text) if price_text else 0.0
                
                rating_text = rating_elem.inner_text().strip() if rating_elem else "0"
                rating = float(rating_text) if rating_text.replace(".", "").isdigit() else 0.0
                
                sales_text = sales_elem.inner_text().strip() if sales_elem else "0"
                sales = self._parse_sales(sales_text)
                
                url = link_elem.get_attribute("href") if link_elem else ""
                if url and not url.startswith("http"):
                    url = "https:" + url
                
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
    
    def _parse_sales(self, text: str) -> int:
        text = text.replace("+", "").replace("万", "0000")
        for char in ["人", "已", "销", " "]:
            text = text.replace(char, "")
        try:
            return int(text)
        except ValueError:
            return 0
