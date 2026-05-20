from pages.base_page import BasePage
import allure

class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.cart_link = page.locator("#cartur")
        self.cart_items = page.locator("#tbodyid tr.success")
        self.total_price = page.locator("#totalp")
        self.products_table = page.locator(".success")
        self.place_order_button = page.locator("//button[text()='Place Order']")

        # Purchase form locators
        self.name_input = page.locator("#name")
        self.country_input = page.locator("#country")
        self.city_input = page.locator("#city")
        self.credit_card_input = page.locator("#card")
        self.card_month = page.locator("#month")
        self.card_year = page.locator("#year")
        self.purchase_button = page.locator("//button[text()='Purchase']")

        # Confirmation modal locators
        self.confirmation_message = page.locator(".sweet-alert  h2")
        self.ok_button = page.locator(".confirm")
        self.receipt_content = page.locator(".lead")

    @allure.step("Open the cart")
    def open_cart(self):
        self.cart_link.click()
        self.page.wait_for_selector(
            "#tbodyid", state="attached"
        )  # Wait for Cartesian table to render

    @allure.step("Get list of products in the cart")
    def get_cart_products(self) -> list[str]:
        try:
            self.cart_items.first.wait_for(timeout=5000)
        except:
            pass
        # returns the cart text data
        return self.cart_items.all_inner_texts()

    @allure.step(
        "Proceed to checkout with name: {name} and test credit card: {credit_card}"
    )
    def do_checkout(self, country: str, city: str, name: str, credit_card: str, month: str, year: str):
        self.place_order_button.click()
        self.name_input.fill(name)
        self.country_input.fill(country)
        self.city_input.fill(city)
        self.credit_card_input.fill(credit_card)
        self.card_month.fill(month)
        self.card_year.fill(year)
        self.purchase_button.click()
        self.confirmation_message.wait_for(state="visible", timeout=5000)
        return self.confirmation_message.is_visible()

    def get_total_price(self) -> int:
        # The website shows total price like this: $360, only we need the numbers
        total_price_text = self.total_price.text_content()

        # Remove any non-digit characters and convert to integer
        int_total__price = int("".join(filter(str.isdigit, total_price_text)))
        return int_total__price

    @allure.step("Delete a product from the cart by its name")
    def delete_product(self, product_name: str):
        self.page.locator(
            f"//td[text()='{product_name}']/following-sibling::td/a[text()='Delete']"
        ).click()
        self.products_table.wait_for(state="hidden")

    @allure.step("Validate receipt data. Country: {country}, City: {city}, Name: {name}, Credit Card: {credit_card}, Month: {month}, Year: {year}")
    def validate_receipt_data(self, country: str, city: str, name: str, credit_card: str, month: str, year: str) -> bool:
        receipt_text = self.receipt_content.text_content()
        # Note: Demoblaze receipt text only displays ID, Amount, Card Number, Name, and Date.
        # It does not include country, city, month, or year.
        assert name in receipt_text, f"Name '{name}' not found in receipt: {receipt_text}"
        assert credit_card in receipt_text, f"Credit card '{credit_card}' not found in receipt: {receipt_text}"
        return True

