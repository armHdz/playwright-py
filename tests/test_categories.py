import allure
from pages.home_page import HomePage
from config import settings

@allure.title("Filter Products by Category")
def test_category_filtering(page):
    home_page = HomePage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # By default it shows some products (usually a mix, largely phones)
    default_products = home_page.get_visible_products()
    assert len(default_products) > 0

    # Select Laptops category and verify expected products are shown
    home_page.select_category("Laptops")
    laptops_products = home_page.get_visible_products()
    assert len(laptops_products) > 0
    # Sony vaio i5, MacBook air, Dell i7 8gb, etc.
    assert any("Sony vaio" in p or "MacBook" in p or "Dell" in p for p in laptops_products)

    # Select Monitors category and verify expected products are shown
    home_page.select_category("Monitors")
    monitors_products = home_page.get_visible_products()
    assert len(monitors_products) > 0
    # Apple monitor 24, ASUS Full HD
    assert any("monitor" in p.lower() or "asus" in p.lower() for p in monitors_products)
