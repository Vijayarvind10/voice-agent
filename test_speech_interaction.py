import os
import time
from playwright.sync_api import sync_playwright, expect

def test_speech_interaction():
    with sync_playwright() as p:
        # Launch Chromium with fake media stream to bypass permission prompts
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream"
            ]
        )
        context = browser.new_context()
        page = context.new_page()

        # Block external CDN assets to avoid navigation timeouts
        page.route("**/*.{png,jpg,jpeg,woff,woff2,ttf,svg,css}", lambda route: route.abort())
        page.route("**/lenis.min.js", lambda route: route.abort())
        page.route("**/gsap.min.js", lambda route: route.abort())
        page.route("**/ScrollTrigger.min.js", lambda route: route.abort())

        # Navigate to the local index.html file
        filepath = os.path.abspath('index.html')
        page.goto(f"file://{filepath}")

        # Wait for the page to load
        page.wait_for_selector("#commandInput")

        # Test inputting a command that triggers classify()
        input_box = page.locator("#commandInput")
        input_box.fill("Set a timer for 5 minutes")

        # Click the "Run" button to trigger the pipeline
        run_btn = page.locator("#speakBtn")
        run_btn.click()

        # Wait for the logs to update to confirm classification worked
        # The first stage is INVOCATION, then ASR, then ATTENTION
        page.wait_for_selector(".log-line .stage-tag", timeout=5000)

        # Take a screenshot of the result
        os.makedirs("/home/jules/verification", exist_ok=True)
        page.screenshot(path="/home/jules/verification/classification_test.png")

        browser.close()

if __name__ == "__main__":
    test_speech_interaction()
