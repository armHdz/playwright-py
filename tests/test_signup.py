import allure
import uuid
from pages.signup_page import SignupPage
from config import settings

@allure.title("Successful User Registration")
def test_successful_signup(page):
    signup_page = SignupPage(page)

    #Navigate to home page and click on signup
    signup_page.navigate(settings.base_url)
    
    #Generate random username and password
    unique_username = f"test_user_{uuid.uuid4().hex[:8]}"
    message = signup_page.register_user(unique_username, "password123")
    
    #Validate the user is signed up successfully
    assert message == "Sign up successful."
