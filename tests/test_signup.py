import allure
import uuid
from pages.signup_page import SignupPage
from config import settings

@allure.title("Successful User Registration")
def test_successful_signup(page):
    signup_page = SignupPage(page)
    signup_page.navigate(settings.base_url)
    
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    
    message = signup_page.register_user(unique_username, "password123")
    
    assert message == "Sign up successful."
