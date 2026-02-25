import asyncio
from playwright.async_api import async_playwright
import http.server
import socketserver
import threading
import time

PORT = 8083 # Use different port

def run_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

async def main():
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1) # Wait for server to start

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(permissions=['microphone'])
        page = await context.new_page()

        # Inject mock for SpeechRecognition
        await page.add_init_script("""
            window.mockSpeechRecognition = class {
                constructor() {
                    this.continuous = false;
                    this.interimResults = true;
                    this.lang = 'en-US';
                    this.onresult = null;
                    this.onend = null;
                    this.onerror = null;
                    this.onstart = null;
                    this._started = false;
                    this._stopCalled = false;
                }
                start() {
                    console.log('Mock SpeechRecognition started');
                    this._started = true;
                    this._stopCalled = false;
                    setTimeout(() => { if (this.onstart) this.onstart(); }, 500);

                    // Simulate an interim result with high confidence
                    // "Take a screenshot" (should trigger predictive stop)
                    setTimeout(() => {
                        if (!this._started) return;
                        if (this.onresult) {
                            const event = {
                                resultIndex: 0,
                                results: {
                                    length: 1,
                                    item: (index) => this.results[index],
                                    0: {
                                        isFinal: false,
                                        0: { transcript: 'take a screenshot' }
                                    }
                                }
                            };
                            event.results[0][0] = { transcript: 'take a screenshot' };
                            this.onresult(event);
                        }
                    }, 1500);
                }
                stop() {
                    console.log('Mock SpeechRecognition stop() called');
                    this._stopCalled = true;
                    this._started = false;
                    window.lastStopCallTime = Date.now();
                    if (this.onend) this.onend();
                }
            };
            window.SpeechRecognition = window.mockSpeechRecognition;
            window.webkitSpeechRecognition = window.mockSpeechRecognition;
            window.lastStopCallTime = 0;
        """)

        await page.goto(f'http://localhost:{PORT}/index.html')

        print("Clicking mic button...")
        await page.click('#micBtn')

        # Wait for "Listening..." state
        await asyncio.sleep(1)

        # Wait for simulated interim result and potential stop call
        await asyncio.sleep(2)

        # Check if stop() was called
        stop_called = await page.evaluate("() => window.lastStopCallTime > 0")

        if stop_called:
            print("CONFIRMED: Predictive Execution called stop() on interim result.")
        else:
            print("FAILED TO REPRODUCE: Predictive Execution did NOT call stop().")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
