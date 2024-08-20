import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import pytest
from datetime import datetime
import random

# Main breaker for debug parameters
DEBUG = True

if DEBUG:
    # Parameters that can be tweaked for debugging
    DEBUG_HEADLESS = False
    DEBUG_VERBOSE = 2
    DEBUG_SLOWMO = 200
else:
    # Defaults - Don't change these for debugging
    DEBUG_HEADLESS = True
    DEBUG_VERBOSE = 0
    DEBUG_SLOWMO = 0

VODAFONE_IE_HOME = "https://www.vodafone.ie"

# Used for logging activity with timestamps and call stacks
def log(calling_functions: str, text: str) -> None:
    logstr = datetime.now().strftime("[%d/%m/%Y, %H:%M:%S] ") + f"[{calling_functions}] {text}\n"
    with open("log.log",mode="a") as file:
        file.write(logstr)
    if DEBUG_VERBOSE:
        print(logstr)
# TODO2 rewrite this function to be more efficient - there's no need to open and close the file every time (though if it crashes this could be useful?)

# Pytest fixture to create the browser and teardown
@pytest.fixture(scope="session")
def browser():
    t=random.randint(0,100000)
    log("BrowserFixture",f"New browser ({t}) being created...")
    playwright = sync_playwright().start() # Launch Playwright
    browser = playwright.chromium.launch( headless=DEBUG_HEADLESS, slow_mo=DEBUG_SLOWMO ) # Launch Chromium
    yield browser # Pass control back to the calling function
    browser.close() # Close the browser for teardown
    playwright.stop() # Stop Playwright for teardown
    log("BrowserFixture",f"Browser {t} torn down")

@pytest.fixture(scope="function")
def page(browser):
    t=random.randint(0,100000)
    log("PageFixture",f"New context ({t}) being created...")
    context = browser.new_context( record_video_dir = "videos/" )
    page = context.new_page()
    yield page
    log("PageFixture",f"Context {t} torn down. Video at {page.video.path()}")
    context.close()

#@pytest.mark.parametrize("handset_index,plan_index",[(1,0)])
@pytest.mark.parametrize("handset_index,plan_index",[(0,0),(0,1),(0,2),(1,0),(2,0),(3,0),(4,0),(5,0)])
# cycle through six different handsets and three different plans
def test_PAYG_phone(page,handset_index,plan_index):
    log("PAYG Phone Test","Opening Vodafone and rejecting cookies")
    page.goto(VODAFONE_IE_HOME,wait_until="domcontentloaded")         # Navigate to Vodafone website
    page.get_by_role("button", name="Reject").click() # Reject all cookies

    log("PAYG Phone Test","Selecting PAYG phones")
    page.get_by_role("link", name="Pay as you go phones Prepay").click() # Select PAYG phones

    # Select the handset
    log("PAYG Phone Test",f"Selecting phone #{handset_index}")
    page.get_by_role("button").get_by_text("Phone from €").locator("nth="+str(handset_index)).click()
    
    # TODO Check if handset is out of stock here

    log("PAYG Phone Test",f"Selecting no")
    page.get_by_role("link", name="No", exact=True).click()              # Select No for "Are you a Vodafone customer?"
    log("PAYG Phone Test",f"Selecting new number")
    page.get_by_role("link", name="Get a new number").click()            # Select that you would like a new number
    log("PAYG Phone Test",f"Selecting plan")
    page.get_by_role("button", name="Get this plan").locator("nth="+str(plan_index)).click()   # Select the plan specified
    log("PAYG Phone Test",f"Selecting continue to basket")
    page.get_by_role("button", name="Continue to basket").click()        # Continue to the basket
    log("PAYG Phone Test",f"Selecting continue")
    page.get_by_role("button", name="Continue").click()
    log("PAYG Phone Test",f"Selecting go to checkout")
    page.get_by_role("button", name="Go to checkout").click()
    log("PAYG Phone Test",f"Expecting checkout")
    expect(page.locator("li").filter(has_text="Secure Checkout")).to_be_visible()

    return
# todo add 'expect' statements between most of these so the test registers as failed not broken