import time
import random
import os
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
from fake_useragent import UserAgent

# Suppress popups
os.environ["XDG_SESSION_TYPE"] = "x11"
os.environ["BROWSER"] = "/bin/true"

# Log and failure paths
LOG_FILE = Path.home() / "maps-bot" / "maps_requests.log"
FAILURE_SCREENSHOT_DIR = Path.home() / "maps-bot" / "failures"
FAILURE_SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

search_queries = ["Eunoia Medispa Salinas"]
origins = [
    "Seaside CA", "Monterey CA", "Marina CA", "Natividad Medical Center",
    "Hartnell College, Salinas", "Del Monte Shopping Center, Monterey",
    "Laurel Heights Salinas", "Boronda CA", "East Garrison, CA"
]

DIRECTIONS_URL = "https://www.google.com/maps/dir/?api=1&destination=Eunoia+Medispa+Salinas"

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} — {message}\n")

def random_user_agent():
    return UserAgent().random

def simulate_direction(context, query, origin, index):
    page = context.new_page()
    try:
        direction_url = f"https://www.google.com/maps/dir/?api=1&origin={origin.replace(' ', '+')}&destination=Eunoia+Medispa+Salinas"
        page.goto(direction_url, timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        try:
            xdg_btn = page.locator("button:has-text('Cancel')")
            xdg_btn.wait_for(timeout=4000)
            if xdg_btn.is_visible():
                xdg_btn.click()
                log("✅ Dismissed xdg-open popup")
        except:
            log("ℹ️ No xdg-open popup appeared")

        try:
            cookie_btn = page.locator('button:has-text("Accept all")')
            if cookie_btn.is_visible():
                cookie_btn.click()
                log("✅ Accepted cookies")
        except:
            log("ℹ️ No cookie prompt")

        try:
            popup_btn = page.locator("button:has-text('Go back to web')")
            popup_btn.wait_for(timeout=4000)
            popup_btn.click()
            log("✅ Dismissed mobile app popup")
        except TimeoutError:
            log("ℹ️ No mobile app popup appeared")

        page.wait_for_timeout(2000)

        try:
            start_input = page.locator("input[aria-label*='Choose starting point']")
            start_input.wait_for(timeout=10000)
            start_input.click()
            page.wait_for_timeout(1000)
            start_input.fill(origin)
            log(f"✅ Filled origin: {origin}")
            page.keyboard.press("Enter")
            page.wait_for_timeout(8000)
        except:
            log("⚠️ Could not fill origin input")

    except Exception as e:
        log(f"❌ Failed: {e}")
        try:
            screenshot_path = FAILURE_SCREENSHOT_DIR / f"failure_{index}.png"
            page.screenshot(path=str(screenshot_path))
        except Exception as ss:
            log(f"⚠️ Screenshot failed: {ss}")
    finally:
        page.close()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=[
        "--start-maximized",
        "--disable-features=ExternalProtocolDialog,IntentPicker",
        "--disable-external-intent-requests",
        "--no-default-browser-check",
        "--no-experiments",
    ])
    context = browser.new_context(user_agent=random_user_agent(), viewport={"width": 1280, "height": 1024})

    for idx, origin in enumerate(origins):
        query = search_queries[0]
        log(f"Simulating directions for '{query}' from '{origin}'")
        simulate_direction(context, query, origin, idx)

    browser.close()
