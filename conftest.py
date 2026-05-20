import os
import pytest
import allure
from playwright.sync_api import Page

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        page = item.funcargs.get("page")
        if page:
            try:
                screenshot = page.screenshot(timeout=5000)
                name = "screenshot-on-failure" if rep.failed else "screenshot-on-success"
                allure.attach(
                    screenshot,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Failed to take screenshot: {e}")

def pytest_addoption(parser):
        parser.addoption(
            "--env", action="store", default="dev", help="Environment to run tests against (e.g., dev, qa, prod)"
        )

@pytest.fixture(autouse=True, scope="session")
def set_env(request):
    env = request.config.getoption("--env")
    os.environ["ENV"] = env