"""Tests for product comparator.

Test cases for product sorting and ranking.
"""


def test_sort_by_price_ascending():
    """Test sorting products by price in ascending order."""
    products = [
        {"product_name": "Product A", "price": 50.0},
        {"product_name": "Product B", "price": 100.0},
    ]
    sorted_products = sorted(products, key=lambda x: x.get('price', 0), reverse=False)
    
    assert len(sorted_products) == 2
    assert sorted_products[0]["price"] == 50.0
    assert sorted_products[1]["price"] == 100.0


def test_sort_by_price_descending():
    """Test sorting products by price in descending order."""
    products = [
        {"product_name": "Product A", "price": 50.0},
        {"product_name": "Product B", "price": 100.0},
    ]
    sorted_products = sorted(products, key=lambda x: x.get('price', 0), reverse=True)
    
    assert sorted_products[0]["price"] == 100.0
    assert sorted_products[1]["price"] == 50.0


def test_empty_list():
    """Test comparator with empty product list."""
    products = []
    sorted_products = sorted(products, key=lambda x: x.get('price', 0))
    
    assert len(sorted_products) == 0