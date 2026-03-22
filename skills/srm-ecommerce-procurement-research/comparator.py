from typing import List, Tuple
from .scraper.base import Product


class Comparator:
    SORT_BY_PRICE = "price"
    SORT_BY_RATING = "rating"
    SORT_BY_SALES = "sales"
    
    def __init__(self, products: List[Product]):
        self.products = products
    
    def sort(self, by: str = SORT_BY_PRICE, reverse: bool = False) -> List[Product]:
        sort_key = {
            self.SORT_BY_PRICE: lambda p: p.price,
            self.SORT_BY_RATING: lambda p: p.rating,
            self.SORT_BY_SALES: lambda p: p.sales_volume,
        }.get(by, lambda p: p.price)
        
        return sorted(self.products, key=sort_key, reverse=reverse)
    
    def rank(self, by: str = "price") -> List[Tuple[int, Product]]:
        sorted_products = self.sort(by=by, reverse=(by == "rating" or by == "sales"))
        return [(i + 1, p) for i, p in enumerate(sorted_products)]
    
    def compare_price(self) -> Tuple[Product, Product, float]:
        if not self.products:
            return None, None, 0.0  # type: ignore
        
        sorted_by_price = self.sort(by=self.SORT_BY_PRICE)
        cheapest = sorted_by_price[0]
        most_expensive = sorted_by_price[-1]
        savings_pct = ((most_expensive.price - cheapest.price) / most_expensive.price) * 100 if most_expensive.price > 0 else 0
        
        return cheapest, most_expensive, savings_pct
    
    def filter_by_platform(self, platform: str) -> List[Product]:
        return [p for p in self.products if p.platform == platform]
    
    def filter_by_price_range(self, min_price: float = 0, max_price: float = float("inf")) -> List[Product]:
        return [p for p in self.products if min_price <= p.price <= max_price]
    
    def filter_by_rating(self, min_rating: float) -> List[Product]:
        return [p for p in self.products if p.rating >= min_rating]
    
    def filter_by_min_sales(self, min_sales: int) -> List[Product]:
        return [p for p in self.products if p.sales_volume >= min_sales]
