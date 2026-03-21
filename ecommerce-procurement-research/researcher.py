import argparse
import asyncio
from playwright.sync_api import sync_playwright
from typing import List, Optional
from .scraper.base import Product, BaseScraper
from .scraper.taobao_scraper import TaobaoScraper
from .scraper.jd_scraper import JDScraper
from .scraper.pdd_scraper import PddScraper
from .scraper.generic_scraper import GenericScraper
from .comparator import Comparator
from .output_formatter import OutputFormatter


PLATFORM_SCRAPERS = {
    "taobao": TaobaoScraper,
    "jd": JDScraper,
    "pdd": PddScraper,
    "generic": GenericScraper,
}


class ProductResearcher:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def search(
        self,
        keyword: Optional[str] = None,
        url: Optional[str] = None,
        platforms: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Product]:
        if platforms is None:
            platforms = ["taobao", "jd", "pdd"]
        
        all_products = []
        
        for platform in platforms:
            scraper_class = PLATFORM_SCRAPERS.get(platform, GenericScraper)
            scraper = scraper_class()
            
            if url:
                search_url = url
            elif keyword:
                search_url = scraper.search_url(keyword)
            else:
                continue
            
            try:
                products = self._scrape(scraper, search_url, limit)
                all_products.extend(products)
            except Exception as e:
                print(f"Error scraping {platform}: {e}")
                continue
        
        return all_products
    
    def _scrape(self, scraper: BaseScraper, url: str, limit: int) -> List[Product]:
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            if limit:
                page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * 3)")
                page.wait_for_timeout(1000)
            
            products = scraper.extract_products(page)
            return products[:limit]
        finally:
            context.close()
    
    def generate_report(
        self,
        products: List[Product],
        formats: Optional[List[str]] = None,
        search_term: str = "",
        output_dir: str = ".",
    ) -> dict:
        if formats is None:
            formats = ["csv", "md"]
        
        formatter = OutputFormatter(output_dir)
        comparator = Comparator(products)
        ranked = comparator.sort(by="price")
        
        results = {}
        
        if "csv" in formats:
            csv_path = formatter.to_csv(ranked)
            results["csv"] = csv_path
        
        if "md" in formats:
            md_path = formatter.to_markdown(ranked, search_term=search_term)
            results["markdown"] = md_path
        
        return results


def main():
    parser = argparse.ArgumentParser(description="E-commerce Product Research Tool")
    parser.add_argument("--keyword", "-k", help="Search keyword")
    parser.add_argument("--url", "-u", help="Direct URL to scrape")
    parser.add_argument("--platforms", "-p", default="taobao,jd,pdd", help="Comma-separated platforms")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Max products per platform")
    parser.add_argument("--output", "-o", default=".", help="Output directory")
    parser.add_argument("--formats", "-f", default="csv,md", help="Output formats (csv,md)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    
    args = parser.parse_args()
    
    platforms = [p.strip() for p in args.platforms.split(",")]
    formats = [f.strip() for f in args.formats.split(",")]
    
    with ProductResearcher(headless=args.headless) as researcher:
        products = researcher.search(
            keyword=args.keyword,
            url=args.url,
            platforms=platforms,
            limit=args.limit,
        )
        
        results = researcher.generate_report(
            products,
            formats=formats,
            search_term=args.keyword or args.url or "",
            output_dir=args.output,
        )
        
        for format_type, path in results.items():
            print(f"{format_type.upper()}: {path}")


if __name__ == "__main__":
    main()
