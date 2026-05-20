import allure
from pages.login_page import LoginPage
from config import settings
import json
import pytest

def load_login_data():
    with open('data/login_data.json') as f:
        data = json.load(f)
    return data["valid_logins"], data["invalid_logins"]

valid_logins, invalid_logins = load_login_data()

@pytest.mark.parametrize("test_name, username, password, expected_result", valid_logins)
@allure.title("Valid Login Test - {test_name}")
def test_valid_login(page, test_name, username, password, expected_result):
    login_page = LoginPage(page)

    # Navigate to home page
    login_page.navigate(settings.base_url)

    # Login with valid credentials
    login_page.login(username, password)

    # Validate that the user is logged in successfully
    assert login_page.is_logged_in(username) == expected_result

@pytest.mark.parametrize("test_name, username, password, expected_result", invalid_logins)
@allure.title("Invalid Login Test - {test_name}")
def test_invalid_login(page, test_name, username, password, expected_result):
    login_page = LoginPage(page)

    # Navigate to home page
    login_page.navigate(settings.base_url)

    # Attempt to login with invalid credentials
    login_page.login(username, password)

    # Validate that the user is NOT logged in (login should fail)
    assert login_page.is_logged_in(username) == expected_result

@allure.title("User Logout Test")
def test_user_logout(page):
    login_page = LoginPage(page)

    # Navigate to home page and login with valid credentials
    login_page.navigate(settings.base_url)
    login_page.login(settings.username, settings.password)

    # Validate user is logged in before attempting logout
    assert login_page.is_logged_in(settings.username)

    # Perform logout
    login_page.logout()

    # Validate the user is no longer logged in after logout
    assert not login_page.is_logged_in(settings.username)