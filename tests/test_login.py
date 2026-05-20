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
    login_page.navigate(settings.base_url)
    login_page.login(username, password)

    assert login_page.is_logged_in(username) == expected_result

@pytest.mark.parametrize("test_name, username, password, expected_result", invalid_logins)
@allure.title("Invalid Login Test - {test_name}")
def test_invalid_login(page, test_name, username, password, expected_result):
    login_page = LoginPage(page)
    login_page.navigate(settings.base_url)
    login_page.login(username, password)

    assert login_page.is_logged_in(username) == expected_result