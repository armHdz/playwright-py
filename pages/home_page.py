import allure
from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.first_product = page.locator(".card-title a").first
        self.category_phones = page.locator('a:has-text("Phones")')
        self.category_laptops = page.locator('a:has-text("Laptops")')
        self.category_monitors = page.locator('a:has-text("Monitors")')
        self.products_list = page.locator(".card-title a")

        # Contact form locators
        self.contact_link = page.locator('a:has-text("Contact")')
        self.contact_email = page.locator("#recipient-email")
        self.contact_name = page.locator("#recipient-name")
        self.contact_message = page.locator("#message-text")
        self.contact_send_btn = page.locator('button:has-text("Send message")')

    @allure.step("Select the first product in the list")
    def select_first_product(self):
        self.first_product.click()

    @allure.step("Filter products by category: {category_name}")
    def select_category(self, category_name: str):
        if category_name.lower() == "phones":
            self.category_phones.click()
        elif category_name.lower() == "laptops":
            self.category_laptops.click()
        elif category_name.lower() == "monitors":
            self.category_monitors.click()
        self.page.wait_for_timeout(1000)  # wait for network response and DOM update

    @allure.step("Get list of visible product names")
    def get_visible_products(self) -> list[str]:
        try:
            self.first_product.wait_for(timeout=5000)
        except:
            pass
        return self.products_list.all_inner_texts()

    @allure.step("Select a product by name: {product_name}")
    def select_product_by_name(self, product_name: str):
        self.page.locator(f'a:has-text("{product_name}")').click()
        self.page.wait_for_timeout(1000)  # wait for network response and DOM update

    @allure.step("Send a message through the contact form")
    def send_contact_message(self, email, name, message):
        self.contact_link.click()
        self.contact_email.fill(email)
        self.contact_name.fill(name)
        self.contact_message.fill(message)
        alert_messages = []
        self.page.once(
            "dialog",
            lambda dialog: (alert_messages.append(dialog.message), dialog.accept()),
        )
        self.page.wait_for_timeout(500)  # give bootstrap modal time to animate
        self.contact_send_btn.click()
        self.page.wait_for_timeout(
            2000
        )  # Give it 2 seconds for the JS timeout to fire the alert
        return alert_messages[0] if alert_messages else "No alert"
