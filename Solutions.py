import pytest
import pytest_asyncio

from playwright.async_api import async_playwright
from datetime import datetime

@pytest_asyncio.fixture
async def chromium_browser():
    #Setup the browser and return the page object
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_timeout(60000)

        #Yield page object to the test function
        yield page

        #Teardown steps
        await context.close()
        await browser.close()

#Step functions

def get_timestamp():
    #Get the current timestamp
    return datetime.now().strftime("%Y%m%d%H%M%S")

async def navigate_to_page(page):
    #Navigate to the specific page
    print("Navigating to the LeetCode website")
    await page.goto("https://leetcode.com/problems/can-place-flowers/")
    await page.wait_for_load_state("networkidle")
    print("Page loaded")

async def sign_in(page):
    #Sign in to the LeetCode account
    print("Signing in")
    await page.get_by_role("link", name="Sign in").click()
    await page.get_by_role("textbox", name="Username or E-mail").click()
    await page.get_by_role("textbox", name="Username or E-mail").fill("ikarilink")
    await page.get_by_role("textbox", name="Password").click()
    await page.get_by_role("textbox", name="Password").fill("kEJ!IHLWyijt3vjw7onC")
    print("Filled in the credentials")

    await page.wait_for_timeout(7000)
    #iframe = page.frame_locator("iframe[title='Widget containing a Cloudflare security challenge']")
    await page.locator(".container__1Q_2 > div > div").first.click()
    #page.locator("iframe[src=\"https\\:\\/\\/challenges\\.cloudflare\\.com\\/cdn-cgi\\/challenge-platform\\/h\\/b\\/turnstile\\/if\\/ov2\\/av0\\/rcv\\/wm0s0\\/0x4AAAAAAAQrSHUTor4iGTpW\\/light\\/fbE\\/new\\/normal\\/en\\/\"]").content_frame.locator("body").click()

    # Click the Sign In button
    await page.get_by_role("button", name="Sign In").click()
    print("Signed in")

async def select_language(page):
    #Select the language for the solution
    print("Selecting the language")
    #await page.get_by_role("button", name="Sign In").click() #Hack to see if we can force another sign in attempt if it's still in the same page
    await page.screenshot(path=f"screenshots/select_language_screenshot_{get_timestamp()}.png", full_page=True)
    await page.get_by_text("C++").click()
    await page.get_by_text("Python", exact=True).click()
    print("Language selected")

async def insert_code(page):
    #Insert the code into the code editor
    code = """
count = 0
length = len(flowerbed)
for i in range(length):
if flowerbed[i] == 0:
left_empty = (i == 0 or flowerbed[i - 1] == 0)
right_empty = (i == length - 1 or flowerbed[i + 1] == 0)
if left_empty and right_empty:
flowerbed[i] = 1
count += 1
if count >= n:
"""
    await page.locator(".view-lines > div:nth-child(8)").click()
    print("Typing the code")
    await page.keyboard.type(code)
    await page.keyboard.type("return True")
    await page.keyboard.press("Enter")
    for i in range(4):
        await page.keyboard.press("Backspace")
    await page.keyboard.type("return False")

async def run_code(page):
    #Run the code and return the output
    print("Running the code")
    await page.get_by_role("button", name="Run").click()
    await page.wait_for_selector('div[data-e2e-locator="console-result"]')
    print("Code executed")

#Test functions

@pytest.mark.asyncio
async def test_can_navigate_to_leetcode(chromium_browser):
    #Navigate to the LeetCode website
    await navigate_to_page(chromium_browser)
    assert await chromium_browser.title() == "Can Place Flowers - LeetCode"

@pytest.mark.asyncio
async def test_can_sign_in(chromium_browser):
    #Test the sign in process
    await navigate_to_page(chromium_browser)
    await sign_in(chromium_browser)
    await chromium_browser.get_by_role("button", name="avatar").click()
    user_profile_link = await chromium_browser.get_by_role("link", name="ikarilink").inner_text()
    assert "ikarilink" in user_profile_link

@pytest.mark.asyncio
async def test_can_place_flowers(chromium_browser):
    #Test the entire process of signing in, typing in the solution and then get an expected Accepted result upon running the code
    await navigate_to_page(chromium_browser)
    await sign_in(chromium_browser)
    await select_language(chromium_browser)
    await insert_code(chromium_browser)
    await run_code(chromium_browser)
    result = await chromium_browser.locator('div[data-e2e-locator="console-result"]').inner_text()
    assert "Accepted" in result
