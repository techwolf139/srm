# E-commerce Procurement Research

电商产品比价工具，支持淘宝、京东、拼多多等平台的商品数据抓取和对比分析。

## 安装

```bash
pip install playwright pandas
playwright install chromium
```

## 使用

### CLI

```bash
# 关键词搜索
python -m researcher --keyword "机械键盘" --platforms taobao,jd,pdd

# URL 直接访问
python -m researcher --url "https://search.jd.com/search?keyword=机械键盘" --platforms jd

# 指定输出格式和数量
python -m researcher --keyword "iPhone 15手机壳" --limit 30 --formats csv,md
```

### Python API

```python
from researcher import ProductResearcher

with ProductResearcher() as researcher:
    products = researcher.search(
        keyword="机械键盘",
        platforms=["taobao", "jd", "pdd"],
        limit=20
    )
    researcher.generate_report(products, formats=["csv", "md"])
```

## 输出示例

**CSV:**
```csv
rank,product_name,price,rating,sales_volume,platform,source_url
1,iPhone 15 Silicone Case,29.99,4.8,10000,taobao,https://...
```

**Markdown:**
```markdown
# Product Comparison Report

| Rank | Product | Price | Rating | Sales | Platform |
|------|---------|-------|--------|-------|----------|
| 1 | iPhone 15 Case | ¥29.99 | ⭐4.8 | 10k+ | taobao |
```

## 项目结构

```
ecommerce-procurement-research/
├── researcher.py      # 主入口
├── comparator.py      # 产品比较
├── output_formatter.py # 输出格式化
└── scraper/          # 平台适配器
    ├── base.py
    ├── taobao_scraper.py
    ├── jd_scraper.py
    ├── pdd_scraper.py
    └── generic_scraper.py
```

## 支持平台

| 平台 | 域名 |
|------|------|
| 淘宝/天猫 | taobao.com, tmall.com |
| 京东 | jd.com |
| 拼多多 | pdd.com |
| 通用 | 任意 URL |
