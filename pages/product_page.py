from pages.base_page import BasePage
import allure


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_to_cart_button = page.locator("//a[text()='Add to cart']")
        self.product_price = page.locator(".price-container")
        self.product_name = page.locator(".name")

    @allure.step("Get the product price")
    def get_product_price(self):
        # The website shows product price like this: $360, only we need the numbers
        product_price_text = self.product_price.text_content()

        # Remove any non-digit characters and convert to integer
        int_product_price = int("".join(filter(str.isdigit, product_price_text)))
        return int_product_price

    @allure.step("Get the product name")
    def get_product_name(self) -> str:
        return self.product_name.text_content()

    @allure.step("Add the product to the cart")
    def add_to_cart(self):
        with self.page.expect_event("dialog") as dialog_info:
            self.add_to_cart_button.click()
        dialog_info.value.accept()
