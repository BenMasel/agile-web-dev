import threading
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

from app import create_app
from app.extensions import db


class ServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.server = make_server('127.0.0.1', 0, app)
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@pytest.fixture(scope='module')
def live_app():
    app = create_app('config.TestConfig')
    with app.app_context():
        db.create_all()
    server = ServerThread(app)
    server.start()
    time.sleep(0.2)
    yield server.url
    server.shutdown()
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def browser():
    options = Options()
    options.binary_location = '/usr/bin/chromium'
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,900')
    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as exc:
        pytest.skip(f'Chrome WebDriver is unavailable: {exc}')
    yield driver
    driver.quit()


def register(browser, base_url, suffix):
    wait = WebDriverWait(browser, 30)
    browser.get(f'{base_url}/auth?mode=signup')
    wait.until(EC.visibility_of_element_located((By.ID, 'register-email'))).send_keys(
        f'{suffix}@student.uwa.edu.au'
    )
    browser.find_element(By.ID, 'register-student-id').send_keys(suffix)
    browser.find_element(By.ID, 'register-display-name').send_keys(f'Test User {suffix}')
    browser.find_element(By.ID, 'register-password').send_keys('password123')
    browser.find_element(By.ID, 'register-confirm-password').send_keys('password123')
    browser.find_element(By.CSS_SELECTOR, '#signup-form button[type="submit"]').click()
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Settings'))


def test_user_can_register_login_and_logout(browser, live_app):
    register(browser, live_app, '21000001')
    # Use JS click to bypass any overlay/modal that may cover the logout button in CI
    logout_btn = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'form[action$="/logout"] button'))
    )
    browser.execute_script("arguments[0].click();", logout_btn)
    WebDriverWait(browser, 30).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Sign in'))

    browser.get(f'{live_app}/auth?mode=signin')
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, 'login-email'))).send_keys('21000001@student.uwa.edu.au')
    browser.find_element(By.ID, 'login-password').send_keys('password123')
    browser.find_element(By.CSS_SELECTOR, '#signin-form button[type="submit"]').click()
    WebDriverWait(browser, 30).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Test User'))


def test_user_can_search_for_unit_and_open_detail(browser, live_app):
    browser.get(live_app)
    search = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, 'search-input')))
    search.send_keys('CITS3403')
    result = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.result-row')))
    # JS click bypasses child elements intercepting the click in headless Chrome
    browser.execute_script("arguments[0].click();", result)
    WebDriverWait(browser, 30).until(EC.url_contains('/unit/CITS3403'))
    assert 'Agile Web Development' in browser.page_source


def test_user_can_submit_review_and_another_session_can_view_it(browser, live_app):
    register(browser, live_app, '21000002')
    browser.get(f'{live_app}/unit/CITS3403')
    browser.find_element(By.ID, 'rating').send_keys('5')
    browser.find_element(By.ID, 'difficulty').send_keys('3')
    browser.find_element(By.ID, 'workload_hours').send_keys('9')
    browser.find_element(By.ID, 'semester_taken').send_keys('Sem 1 2026')
    browser.find_element(By.ID, 'body').send_keys('Selenium review with practical project advice.')
    browser.find_element(By.CSS_SELECTOR, 'form[action$="/reviews"] button[type="submit"]').click()
    WebDriverWait(browser, 30).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Selenium review with practical project advice.')
    )

    browser.delete_all_cookies()
    browser.get(f'{live_app}/unit/CITS3403')
    assert 'Selenium review with practical project advice.' in browser.page_source


def test_user_can_make_plan_public_and_open_share_link(browser, live_app):
    register(browser, live_app, '21000003')
    browser.get(f'{live_app}/planner')
    browser.execute_script(
        "localStorage.setItem('stUwa_planner_v3', JSON.stringify({"
        "degrees:['BS-CS'], startYear:2026, startSem:1,"
        "plan:{'2026-1':['CITS3403']}, done:['CITS3403'], substitutions:{}}));"
    )
    browser.refresh()
    WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, 'public-plan-toggle'))).click()
    browser.find_element(By.ID, 'save-account-btn').click()
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, 'copy-share-link-btn')))
    share_path = browser.execute_script("return JSON.parse(localStorage.getItem('stUwa_planner_v3')).share_url;")
    browser.get(f'{live_app}{share_path}')
    assert 'CITS3403' in browser.page_source


def test_resources_and_benefits_work_on_mobile_viewport(browser, live_app):
    browser.set_window_size(390, 844)
    browser.get(f'{live_app}/resources')
    assert 'Resources' in browser.page_source
    browser.get(f'{live_app}/benefits')
    assert 'Student Benefits' in browser.page_source
