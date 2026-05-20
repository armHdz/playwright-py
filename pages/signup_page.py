import allure
from pages.base_page import BasePage

class SignupPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.signup_link = page.locator('#signin2')
        self.username_input = page.locator('#sign-username')
        self.password_input = page.locator('#sign-password')
        self.submit_btn = page.locator('button:has-text("Sign up")')

    @allure.step("Register a new user")
    def register_user(self, username, password):
        self.signup_link.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        
        with self.page.expect_event("dialog") as dialog_info:
            self.submit_btn.click()
        
        dialog = dialog_info.value
        message = dialog.message
        dialog.accept()
        await self.page.wait_for_timeout(2000) # Give it 2 seconds for the site to show signed up user
        return message