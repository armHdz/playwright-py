import allure
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from config import settings

from faker import Faker

fake = Faker()

@allure.title("Checkout purchase")
def test_checkout_purchase(page):
    home_page = HomePage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Select a product (e.g., "Samsung galaxy s6")
    home_page.select_first_product()

    # Add the product to the cart
    product_page.add_to_cart()

    # Go to cart page and proceed to checkout
    cart_page.open_cart()
    assert cart_page.do_checkout(
        country=fake.country(),
        city=fake.city(),
        name=settings.card_name,
        credit_card=settings.card_number,
        month=fake.month(),
        year=fake.year()
    )


@allure.title("Full checkout with receipt validation")
def test_full_checkout_with_receipt_validation(page):
    home_page = HomePage(page)
    product_page = ProductPage(page)
    cart_page = CartPage(page)

    country = fake.country()
    city = fake.city()
    month = fake.month()
    year = fake.year()

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Select a product (e.g., "Samsung galaxy s6")
    home_page.select_first_product()

    # Add the product to the cart
    product_page.add_to_cart()

    # Go to cart page and proceed to checkout
    cart_page.open_cart()
    assert cart_page.do_checkout(
        country, city, settings.card_name, settings.card_number, month, year
    )

    # Validate receipt
    assert cart_page.validate_receipt_data(country, city, settings.card_name, settings.card_number, month, year)
