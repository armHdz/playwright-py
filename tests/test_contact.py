import allure
from pages.home_page import HomePage
from config import settings

@allure.title("Send Contact Form Message")
def test_contact_form(page):
    home_page = HomePage(page)

    # Navigate to home page
    home_page.navigate(settings.base_url)

    # Fill and submit the contact form
    alert_message = home_page.send_contact_message(
        email="test_contact_ahc@example.com",
        name="Test User",
        message="This is a test message from the automated testing suite."
    )

    # Validate that the message went through successfully
    assert alert_message == "Thanks for the message!!"
