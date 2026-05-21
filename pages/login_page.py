import allure
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):  #define all locators here
        super().__init__(page)
        self.login_btn = page.locator('#login2')
        self.username_input = page.locator('#loginusername')
        self.password_input = page.locator('#loginpassword')
        self.submit_btn = page.locator('button:has-text("Log in")')
        self.welcome_label = page.locator('#nameofuser')
        self.logout_link = page.locator('#logout2')

    @allure.step("Login with username: {username}")
    def login(self, username, password):  #define all actions here
        self.login_btn.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.page.once("dialog", lambda dialog: dialog.accept()) # Handle invalid login alerts automatically
        self.submit_btn.click()

    @allure.step("Logout")
    def logout(self):
        self.logout_link.click()
        self.page.wait_for_timeout(1000)  # wait for network response and DOM update

    @allure.step("Verify user is logged in")
    def is_logged_in(self, username: str) -> bool: #validate user is logged in successfully
        try:
            self.welcome_label.wait_for(timeout=3000)
            is_logged = self.welcome_label.inner_text().strip() == f"Welcome {username}"
        except Exception:
            is_logged = False
        screenshot = self.page.screenshot()
        allure.attach(screenshot, name="Login State", attachment_type=allure.attachment_type.PNG)
        return is_logged