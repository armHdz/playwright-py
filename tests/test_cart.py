import allure
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from config import settings


@allure.title("Add single product to cart")
def test_add_product_to_cart(page):
    home_page = HomePage(page)
    product_page = ProductPage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Select a product (e.g., "Samsung galaxy s6")
    home_page.select_first_product()

    # Add the product to the cart
    product_page.add_to_cart()

    # validate that the product is actually inside the cart's table
    cart_page = CartPage(page)
    cart_page.open_cart()

    # Check that there is at least one item in the list or a specific item name
    products_in_cart = cart_page.get_cart_products()
    assert len(products_in_cart) > 0, "No products were found in the cart!"


@allure.title("Add multiple products to cart")
def test_add_multiple_products_to_cart(page):
    home_page = HomePage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Navigate to phones category and select product Samsung galaxy s6
    home_page.select_category("phones")
    phone_products = home_page.get_visible_products()
    for phone_name in phone_products:
        if "Samsung galaxy s6" in phone_name:
            home_page.select_product_by_name(phone_name)
            break

    # Get product price
    samsung_price = product_page.get_product_price()

    # Add the product to the cart
    product_page.add_to_cart()

    # Navigate to laptops category and select product MacBook air
    home_page.navigate(settings.base_url)
    home_page.select_category("laptops")
    laptop_products = home_page.get_visible_products()
    for laptop_name in laptop_products:
        if "MacBook air" in laptop_name:
            home_page.select_product_by_name(laptop_name)
            break

    # Get product price
    macbook_price = product_page.get_product_price()

    # Add the product to the cart
    product_page.add_to_cart()

    # validate that the product is actually inside the cart's table
    cart_page.open_cart()

    # Check that there is at least one item in the list or a specific item name
    products_in_cart = cart_page.get_cart_products()
    assert any("Samsung galaxy s6" in item for item in products_in_cart) and any(
        "MacBook air" in item for item in products_in_cart
    ), "Products are not in the cart!"
    assert cart_page.get_total_price() == int(samsung_price) + int(macbook_price), (
        "Total price is not correct!"
    )


@allure.title("Delete product from cart")
def test_delete_product_from_cart(page):
    home_page = HomePage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Select a product (e.g., "Samsung galaxy s6") and get its name
    home_page.select_first_product()
    product_name = product_page.get_product_name()

    # Add the product to the cart
    product_page.add_to_cart()

    # validate that the product is actually inside the cart's table
    cart_page.open_cart()

    # Check that there is at least one item in the list or a specific item name
    products_in_cart = cart_page.get_cart_products()
    assert len(products_in_cart) > 0, "No products were found in the cart!"

    # Validate product is the same as added to cart
    assert any(f"{product_name}" in item for item in products_in_cart), (
        "Product is not in the cart!"
    )

    # Delete the product from the cart
    cart_page.delete_product(product_name)

    # Validate that the product is no longer in the cart
    products_in_cart = cart_page.get_cart_products()
    assert len(products_in_cart) == 0, "Product is still in the cart!"
