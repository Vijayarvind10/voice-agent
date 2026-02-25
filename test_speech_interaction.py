import asyncio
from playwright.async_api import async_playwright
import http.server
import socketserver
import threading
import time

PORT = 8080

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
                    this.interimResults = false;
                    this.lang = 'en-US';
                    this.onresult = null;
                    this.onend = null;
                    this.onerror = null;
                    this.onstart = null;
                    this._started = false;
                }
                start() {
                    console.log('Mock SpeechRecognition started');
                    this._started = true;
                    if (this.onstart) this.onstart();

                    // Simulate no result if we want to reproduce the bug
                    // Or simulate result to verify it works

                    // Let's simulate a delay then a result
                    setTimeout(() => {
                        if (!this._started) return;
                        if (this.onresult) {
                            const event = {
                                resultIndex: 0,
                                results: {
                                    length: 1,
                                    item: (index) => this.results[index],
                                    0: {
                                        isFinal: true,
                                        0: { transcript: 'test command' }
                                    }
                                }
                            };
                            // Add array accessors which are present in real API
                            event.results[0][0] = { transcript: 'test command' };
                            this.onresult(event);
                        }
                        this.stop();
                    }, 1000);
                }
                stop() {
                    console.log('Mock SpeechRecognition stopped');
                    this._started = false;
                    if (this.onend) this.onend();
                }
            };
            window.SpeechRecognition = window.mockSpeechRecognition;
            window.webkitSpeechRecognition = window.mockSpeechRecognition;
        """)

        await page.goto(f'http://localhost:{PORT}/index.html')

        # Check initial state
        print("Initial input value:", await page.input_value('#commandInput'))

        # Click mic button
        print("Clicking mic button...")
        await page.click('#micBtn')

        # Wait a bit for simulation
        await asyncio.sleep(2)

        # Check if input was updated
        input_value = await page.input_value('#commandInput')
        print("Input value after speech:", input_value)

        if input_value == 'test command':
            print("SUCCESS: Input updated correctly.")
        else:
            print("FAILURE: Input not updated.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
