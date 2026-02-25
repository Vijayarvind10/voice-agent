"""
Real Time Voice MCP — Backend Server
FastAPI + WebSocket with 13 MCP servers, TTS, multi-command chaining, conversational memory.
"""

import asyncio, json, subprocess, re, random, string, urllib.parse, os, platform
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Real Time Voice MCP")

# Restricted CORS origins for security - allow only local development origins
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Regex Patterns & Intent Config ────────────────────────────────────
INTENT_CONFIG = []
INTENT_MAP = {}
try:
    with open("static/intents.json", "r") as f:
        INTENT_CONFIG = json.load(f)
    for intent in INTENT_CONFIG:
        intent["compiled_triggers"] = [re.compile(p, re.IGNORECASE) for p in intent["triggers"]]
        if "extraction" in intent:
            intent["compiled_extraction"] = {}
            for key, pattern in intent["extraction"].items():
                intent["compiled_extraction"][key] = re.compile(pattern, re.IGNORECASE)
        INTENT_MAP[intent["id"]] = intent
except Exception as e:
    print(f"Error loading intents.json: {e}")

# ── Handlers ──────────────────────────────────────────────────────────
def build_response(intent, params=None, confidence=None):
    return {
        "supported": intent["properties"]["supported"],
        "intent": intent["id"],
        "confidence": confidence or intent["properties"]["confidence"],
        "routeType": intent["properties"]["routeType"],
        "servers": intent["properties"]["servers"],
        "privacyClass": intent["properties"]["privacyClass"],
        "params": params or {}
    }

def handle_set_timer(text, intent):
    ext = intent.get("compiled_extraction", {})
    m = ext.get("duration_regex").search(text)
    if m:
        dur = f"{m.group(1)} {m.group(2)}s"
        raw = int(m.group(1))
        unit = m.group(2)
        secs = raw * (3600 if 'hour' in unit or 'hr' in unit else 60 if 'min' in unit else 1)
        return build_response(intent, params={"duration": dur, "seconds": secs})
    return {
        "supported": True, "intent": "MISSING_SLOT", "confidence": 0.90,
        "routeType": "local", "servers": [], "privacyClass": "local_safe",
        "params": {"slot": "timer_duration", "message": "For how long?"}
    }

def handle_play_music(text, intent):
    query = intent["compiled_extraction"]["removal_regex"].sub('', text).strip()
    return build_response(intent, params={"query": query or "jazz"})

def handle_get_weather(text, intent):
    m = intent["compiled_extraction"]["location_regex"].search(text)
    loc = m.group(1).strip() if m else ""
    return build_response(intent, params={"location": loc})

def handle_volume_control(text, intent):
    ext = intent["compiled_extraction"]
    m = ext["level_regex"].search(text)
    level = int(m.group(1)) if m else None
    mute = bool(ext["mute_regex"].search(text) and not ext["unmute_regex"].search(text))
    unmute = bool(ext["unmute_regex"].search(text))
    return build_response(intent, params={"level": level, "mute": mute, "unmute": unmute})

def handle_create_note(text, intent):
    body = intent["compiled_extraction"]["body_removal_regex"].sub('', text).strip()
    return build_response(intent, params={"body": body or "New note from Voice MCP"})

def handle_create_reminder(text, intent):
    body = intent["compiled_extraction"]["body_removal_regex"].sub('', text).strip()
    return build_response(intent, params={"body": body or "Voice MCP reminder"})

def handle_open_finder(text, intent):
    m = intent["compiled_extraction"]["folder_regex"].search(text)
    folder = m.group(1) if m else "Finder"
    return build_response(intent, params={"folder": folder})

def handle_web_search(text, intent):
    query = intent["compiled_extraction"]["query_removal_regex"].sub('', text).strip()
    return build_response(intent, params={"query": query or "search"})

def handle_open_maps(text, intent):
    query = intent["compiled_extraction"]["query_removal_regex"].sub('', text).strip()
    return build_response(intent, params={"query": query or "current location"})

def handle_open_app(text, intent):
    m = intent["compiled_triggers"][0].search(text)
    app_name = m.group(1) if m else "Finder"
    return build_response(intent, params={"app": app_name})

def handle_calculate(text, intent):
    return build_response(intent, params={"expression": text})

def handle_define_word(text, intent):
    word = intent["compiled_extraction"]["word_removal_regex"].sub('', text).strip()
    return build_response(intent, params={"word": word})

def handle_convert_currency(text, intent):
    return build_response(intent, params={"query": text})

INTENT_HANDLERS = {
    "SET_TIMER": handle_set_timer,
    "PLAY_MUSIC": handle_play_music,
    "GET_WEATHER": handle_get_weather,
    "VOLUME_CONTROL": handle_volume_control,
    "CREATE_NOTE": handle_create_note,
    "CREATE_REMINDER": handle_create_reminder,
    "OPEN_FINDER": handle_open_finder,
    "WEB_SEARCH": handle_web_search,
    "OPEN_MAPS": handle_open_maps,
    "OPEN_APP": handle_open_app,
    "CALCULATE": handle_calculate,
    "DEFINE_WORD": handle_define_word,
    "CONVERT_CURRENCY": handle_convert_currency
}


# ── MCP Server Registry ──────────────────────────────────────────────
SERVERS = [
    {"id": "com.apple.timer.mcp",      "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.calendar.mcp",   "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.messages.mcp",   "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.notes.mcp",      "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.reminders.mcp",  "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.volume.mcp",     "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.finder.mcp",     "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.screenshot.mcp", "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.clipboard.mcp",  "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.systeminfo.mcp", "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.google.youtubemusic",  "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.apple.maps.mcp",       "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.apple.weather.mcp",    "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.apple.websearch.mcp",  "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.apple.clock.mcp",      "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.apple.calculator.mcp", "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.entertainment.jokes.mcp", "scope": "LOCAL", "needsNetwork": False},
    {"id": "com.entertainment.quotes.mcp", "scope": "LOCAL", "needsNetwork": False},
    {"id": "com.tools.random.mcp",     "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.reference.dictionary.mcp", "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.finance.currency.mcp", "scope": "REMOTE", "needsNetwork": True},
    {"id": "com.network.ip.mcp",       "scope": "LOCAL",  "needsNetwork": False},
    {"id": "com.system.uptime.mcp",    "scope": "LOCAL",  "needsNetwork": False},
]

# ── Conversation Memory ──────────────────────────────────────────────
conversation_history = []  # [{turn, command, intent, response, timestamp}]
MAX_HISTORY = 20

# ── Helpers ───────────────────────────────────────────────────────────
def uid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def wake_score(cmd: str) -> float:
    return min(0.98, 0.91 + (len(cmd) % 5) * 0.01)

def normalise(s: str) -> str:
    c = re.sub(r'\s+', ' ', s.strip())
    return c[0].lower() + c[1:] if c else ""

def escape_osascript(s: str) -> str:
    """Escape user input for safe embedding in AppleScript strings."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

def run_osascript(script: str) -> str:
    try:
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or r.stderr.strip() or "ok"
    except Exception as e:
        return str(e)

def run_cmd(args: list, timeout=5) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip() or "ok"
    except Exception as e:
        return str(e)

def run_open(url: str) -> str:
    try:
        subprocess.Popen(["open", url])
        return "opened"
    except Exception as e:
        return str(e)

# ── TTS State ─────────────────────────────────────────────────────────
tts_process = None

def kill_tts():
    global tts_process
    if tts_process and tts_process.poll() is None:
        tts_process.kill()
        tts_process = None

def speak(text: str):
    """TTS via macOS say command (non-blocking)."""
    global tts_process
    kill_tts() # Stop any ongoing speech before starting a new one
    clean = re.sub(r'[^\w\s.,!?\'-]', '', text)[:200]
    tts_process = subprocess.Popen(["say", "-v", "Samantha", clean])


# ── Intent Classification ─────────────────────────────────────────────
def classify(text: str, session_state: dict = None) -> dict:
    t = text.lower()
    state = session_state or {}

    # Handle awaiting slot for timer duration
    if state.get("awaiting_slot") == "timer_duration":
        timer_intent = INTENT_MAP.get("SET_TIMER")
        if timer_intent:
            ext = timer_intent["compiled_extraction"]
            dur_re = ext["duration_regex"]
            num_re = ext["numeric_regex"]

            # Duration match
            m = dur_re.search(t)
            if m:
                dur = f"{m.group(1)} {m.group(2)}s"
                raw = int(m.group(1))
                unit = m.group(2)
                secs = raw * (3600 if 'hour' in unit or 'hr' in unit else 60 if 'min' in unit else 1)
                return build_response(timer_intent, params={"duration": dur, "seconds": secs}, confidence=0.98)

            # Numeric match
            m2 = num_re.search(t)
            if m2:
                dur = f"{m2.group(1)} minutes"
                secs = int(m2.group(1)) * 60
                return build_response(timer_intent, params={"duration": dur, "seconds": secs}, confidence=0.96)

        # Fall through

    # Iterate intents
    for intent in INTENT_CONFIG:
        # Check if ALL triggers match
        if intent.get("compiled_triggers") and all(regex.search(t) for regex in intent["compiled_triggers"]):
            handler = INTENT_HANDLERS.get(intent["id"])
            if handler:
                return handler(t, intent)
            else:
                return build_response(intent)

    return {
        "supported": False, "intent": "UNSUPPORTED", "confidence": 0.58,
        "routeType": "none", "servers": [], "privacyClass": "unknown", "params": {}
    }


# ── Privacy & Route ───────────────────────────────────────────────────
def privacy_check(plan, privacy_mode):
    if plan["privacyClass"] == "external_search" and privacy_mode == "ON":
        return {"approved": False, "label": "BLOCKED · privacy mode ON"}
    if plan["routeType"] == "local":  return {"approved": True, "label": "LOCAL · approved"}
    if plan["routeType"] == "pcc":    return {"approved": True, "label": "PCC · approved"}
    if plan["routeType"] == "remote": return {"approved": True, "label": "REMOTE · approved"}
    return {"approved": False, "label": "BLOCKED · unsupported"}

def route_check(plan, network_mode):
    if plan["routeType"] == "none":
        return {"ok": False, "routeType": "none", "label": "no route", "servers": []}
    if plan["routeType"] == "remote" and network_mode == "OFFLINE":
        return {"ok": False, "routeType": "remote", "label": "REMOTE · network unavailable", "servers": plan["servers"]}
    return {"ok": True, "routeType": plan["routeType"],
            "label": plan["routeType"].upper() + " route", "servers": plan["servers"]}


# ── Real Execution ────────────────────────────────────────────────────
def execute(plan: dict) -> dict:
    intent = plan["intent"]
    p = plan["params"]

    if intent == "MISSING_SLOT":
        return {"log": "dialogue · clarifying", "entityId": f"dlg_{uid()}", "response": p.get("message", "Can you clarify?")}

    if intent == "REPEAT_LAST":
        if len(conversation_history) > 1:
            last = conversation_history[-1]
            return {"log": f"replay · {last['intent']}", "entityId": f"replay_{uid()}",
                    "response": f"Repeating: {last['response']}"}
        return {"log": "no history", "entityId": "none", "response": "No previous command to repeat"}

    if intent == "RECALL_HISTORY":
        if conversation_history:
            recent = conversation_history[-3:]
            summary = " → ".join([h["intent"] for h in recent])
            return {"log": f"history · {len(conversation_history)} turns", "entityId": f"hist_{uid()}",
                    "response": f"Recent: {summary}"}
        return {"log": "empty history", "entityId": "none", "response": "No command history yet"}

    if intent == "SET_TIMER":
        secs = p.get("seconds", 600)
        dur = p.get("duration", "10 minutes")
        run_osascript(f'display notification "Timer set for {dur}" with title "Voice MCP" sound name "Tink"')
        subprocess.Popen(["bash", "-c",
            f'sleep {secs} && osascript -e \'display notification "⏱ Timer done!" with title "Voice MCP" sound name "Glass"\''])
        return {"log": f"timer · armed for {dur}", "entityId": f"timer_{uid()}",
                "response": f"Timer set for {dur}"}

    if intent == "PLAY_MUSIC":
        q = urllib.parse.quote_plus(p.get("query", "jazz"))
        run_open(f"https://music.youtube.com/search?q={q}")
        return {"log": f"youtube_music · '{p.get('query','jazz')}'", "entityId": f"music_{uid()}",
                "response": f"Opening YouTube Music — {p.get('query','jazz')}"}

    if intent == "GET_WEATHER":
        loc = p.get("location", "")
        loc_param = urllib.parse.quote_plus(loc) if loc else ""
        try:
            r = subprocess.run(["curl", "-s", f"https://wttr.in/{loc_param}?format=3"], capture_output=True, text=True, timeout=5)
            weather = r.stdout.strip() or "Weather data unavailable"
        except:
            weather = "Could not fetch weather"
        return {"log": f"weather · {loc or 'local'}", "entityId": f"weather_{uid()}",
                "response": weather}

    if intent == "TAKE_SCREENSHOT":
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.expanduser(f"~/Desktop/screenshot_{ts}.png")
        run_cmd(["screencapture", "-x", path])
        return {"log": f"screenshot · {path}", "entityId": f"ss_{uid()}",
                "response": f"Screenshot saved to Desktop"}

    if intent == "CLIPBOARD":
        content = run_cmd(["pbpaste"])
        preview = content[:100] + ("..." if len(content) > 100 else "")
        return {"log": "clipboard · read", "entityId": f"clip_{uid()}",
                "response": f"Clipboard: {preview}" if content else "Clipboard is empty"}

    if intent == "SYSTEM_INFO":
        battery = run_cmd(["pmset", "-g", "batt"])
        bat_match = re.search(r'(\d+)%', battery)
        bat_pct = bat_match.group(1) + "%" if bat_match else "N/A"
        mem = run_cmd(["sysctl", "-n", "hw.memsize"])
        try: mem_gb = f"{int(mem) / (1024**3):.0f}GB"
        except: mem_gb = "N/A"
        cpu = run_cmd(["sysctl", "-n", "machdep.cpu.brand_string"])
        disk = run_cmd(["df", "-h", "/"])
        disk_match = re.search(r'(\d+)%', disk)
        disk_used = disk_match.group(0) if disk_match else "N/A"
        return {"log": "sysinfo · fetched", "entityId": f"sys_{uid()}",
                "response": f"Battery: {bat_pct} · RAM: {mem_gb} · CPU: {cpu[:40]} · Disk: {disk_used} used"}

    if intent == "VOLUME_CONTROL":
        if p.get("mute"):
            run_osascript('set volume with output muted')
            return {"log": "volume · muted", "entityId": f"vol_{uid()}", "response": "Volume muted"}
        if p.get("unmute"):
            run_osascript('set volume without output muted')
            return {"log": "volume · unmuted", "entityId": f"vol_{uid()}", "response": "Volume unmuted"}
        level = p.get("level")
        if level is not None:
            apple_vol = max(0, min(100, level)) / 100 * 7
            run_osascript(f'set volume output volume {level}')
            return {"log": f"volume · set to {level}%", "entityId": f"vol_{uid()}", "response": f"Volume set to {level}%"}
        return {"log": "volume · no action", "entityId": f"vol_{uid()}", "response": "Say 'set volume to 50' or 'mute'"}

    if intent == "CREATE_NOTE":
        body = escape_osascript(p.get("body", "Note from Voice MCP"))
        run_osascript(f'''
            tell application "Notes"
                activate
                tell account "iCloud"
                    make new note at folder "Notes" with properties {{body:"{body}"}}
                end tell
            end tell
        ''')
        return {"log": f"notes · created", "entityId": f"note_{uid()}",
                "response": f"Note created: {body[:60]}"}

    if intent == "CREATE_REMINDER":
        body = escape_osascript(p.get("body", "Reminder"))
        run_osascript(f'''
            tell application "Reminders"
                activate
                tell list "Reminders"
                    make new reminder with properties {{name:"{body}"}}
                end tell
            end tell
        ''')
        return {"log": f"reminders · added", "entityId": f"rem_{uid()}",
                "response": f"Reminder added: {body[:60]}"}

    if intent == "OPEN_FINDER":
        folder = p.get("folder", "Finder").lower()
        paths = {"downloads": "~/Downloads", "documents": "~/Documents", "desktop": "~/Desktop", "home": "~", "finder": "~"}
        path = os.path.expanduser(paths.get(folder, "~"))
        run_open(path)
        return {"log": f"finder · {folder}", "entityId": f"finder_{uid()}",
                "response": f"Opened {folder.capitalize()} folder"}

    if intent == "FOLLOWUP_FROM_MESSAGE":
        run_open("/System/Applications/Messages.app")
        run_open("/System/Applications/Calendar.app")
        return {"log": "messages + calendar · opened", "entityId": f"followup_{uid()}",
                "response": "Opened Messages and Calendar"}

    if intent == "WEB_SEARCH":
        q = urllib.parse.quote_plus(p.get("query", "search"))
        run_open(f"https://www.google.com/search?q={q}")
        return {"log": f"web_search · '{p.get('query','')}'", "entityId": f"search_{uid()}",
                "response": f"Searching for '{p.get('query','')}'"}

    if intent == "OPEN_MAPS":
        q = urllib.parse.quote_plus(p.get("query", ""))
        run_open(f"https://maps.apple.com/?q={q}")
        return {"log": f"maps · '{p.get('query','')}'", "entityId": f"maps_{uid()}",
                "response": f"Opening Apple Maps — {p.get('query','')}"}

    if intent == "SEND_MESSAGE":
        run_open("/System/Applications/Messages.app")
        return {"log": "messages · opened", "entityId": f"msg_{uid()}", "response": "Opening Messages"}

    if intent == "CREATE_EVENT":
        run_open("/System/Applications/Calendar.app")
        run_osascript('tell application "Calendar" to activate')
        return {"log": "calendar · opened", "entityId": f"event_{uid()}", "response": "Opening Calendar"}

    if intent == "OPEN_APP":
        app = p.get("app", "Finder")
        subprocess.Popen(["open", "-a", app.capitalize()])
        return {"log": f"{app} · launched", "entityId": f"app_{uid()}", "response": f"Opening {app.capitalize()}"}

    if intent == "GET_DATE_TIME":
        now = run_cmd(["date"])
        return {"log": "clock · fetched", "entityId": f"time_{uid()}", "response": f"It is {now}"}

    if intent == "CALCULATE":
        # Safe eval for demo purposes
        expr = p.get("expression", "")
        # Replace common words with operators
        expr = expr.lower().replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/").replace("over", "/")
        # Very basic sanitization
        clean_expr = re.sub(r'[^\d+\-*/().]', '', expr)
        try:
            # pylint: disable=eval-used
            res = eval(clean_expr, {"__builtins__": None}, {})
            return {"log": "calc · computed", "entityId": f"calc_{uid()}", "response": f"The answer is {res}"}
        except:
             return {"log": "calc · error", "entityId": f"err_{uid()}", "response": "I couldn't calculate that"}

    if intent == "TELL_JOKE":
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I ordered a chicken and an egg from Amazon. I'll let you know.",
            "What is a cloud's favourite number? Seven. Because seven ate nine, and it was overcast.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised."
        ]
        joke = random.choice(jokes)
        return {"log": "joke · told", "entityId": f"joke_{uid()}", "response": joke}

    if intent == "GET_QUOTE":
        quotes = [
            "The only way to do great work is to love what you do. — Steve Jobs",
            "Code is like humor. When you have to explain it, it’s bad. — Cory House",
            "Simplicity is the soul of efficiency. — Austin Freeman",
            "Talk is cheap. Show me the code. — Linus Torvalds"
        ]
        quote = random.choice(quotes)
        return {"log": "quote · fetched", "entityId": f"quote_{uid()}", "response": quote}

    if intent == "FLIP_COIN":
        res = random.choice(["Heads", "Tails"])
        return {"log": "coin · flipped", "entityId": f"coin_{uid()}", "response": res}

    if intent == "ROLL_DIE":
        res = str(random.randint(1, 6))
        return {"log": "die · rolled", "entityId": f"die_{uid()}", "response": res}

    if intent == "DEFINE_WORD":
        w = p.get("word", "unknown")
        # Mock definition
        return {"log": "dictionary · defined", "entityId": f"def_{uid()}", "response": f"Definition of {w}: A word used in this demo."}

    if intent == "CONVERT_CURRENCY":
        # Mock conversion
        return {"log": "currency · converted", "entityId": f"curr_{uid()}", "response": "1 USD is approximately 0.94 EUR"}

    if intent == "GET_IP":
        # Try to get local IP
        try:
            # This works on macOS/Linux usually
            ip = run_cmd(["ifconfig"])
            # Extract first non-loopback IP for demo (very rough regex)
            m = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip)
            my_ip = m.group(1) if m else "127.0.0.1"
            if my_ip == "127.0.0.1":
                # Try another way
                my_ip = subprocess.getoutput("hostname -I").split()[0]
        except:
            my_ip = "Unknown"
        return {"log": "ip · fetched", "entityId": f"ip_{uid()}", "response": f"Your IP address is {my_ip}"}

    if intent == "GET_UPTIME":
        up = run_cmd(["uptime"])
        # Format: 10:00  up 1 day, 20 mins, 2 users, load averages: ...
        return {"log": "uptime · fetched", "entityId": f"uptime_{uid()}", "response": f"System status: {up.split(',')[0]}"}

    return {"log": "no-op", "entityId": "none", "response": "I couldn't handle that command"}


# ── Multi-Command Splitter ────────────────────────────────────────────
def split_commands(text: str) -> list:
    """Split "do X and then Y" into multiple commands."""
    parts = re.split(r'\s+(?:and then|and also|and|then|also)\s+', text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


# ── WebSocket Pipeline ────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    # Send server list on connect
    await ws.send_json({"type": "servers", "servers": SERVERS})
    session_state = {"awaiting_slot": None}
    try:
        while True:
            data = await ws.receive_json()
            cmd = data.get("command", "").strip()
            privacy = data.get("privacy", "ON")
            network = data.get("network", "ONLINE")
            tts = data.get("tts", True)

            if not cmd and data.get("type") != "barge_in":
                await ws.send_json({"type": "error", "message": "Empty command"})
                continue

            # Handle Barge-In
            if data.get("type") == "barge_in":
                kill_tts()
                continue

            # Multi-command chaining
            commands = split_commands(normalise(cmd))
            is_chain = len(commands) > 1
            if is_chain:
                await ws.send_json({"type": "chain", "count": len(commands),
                                     "commands": commands})

            for ci, single_cmd in enumerate(commands):
                if is_chain:
                    await ws.send_json({"type": "chain_step", "index": ci, "command": single_cmd})

                # Stage 1: INVOCATION
                score = wake_score(single_cmd)
                await ws.send_json({"type": "stage", "index": 0, "id": "invocation",
                                    "status": "ok", "text": f"confidence: {score:.2f} → WAKE"})
                await asyncio.sleep(0.06)

                # Stage 2: ASR
                transcript = normalise(single_cmd)
                await ws.send_json({"type": "stage", "index": 1, "id": "asr",
                                    "status": "ok", "text": f"\u201c{transcript}\u201d"})
                await asyncio.sleep(0.06)

                # Stage 3: ATTENTION
                plan = classify(transcript, session_state)
                att_st = "pcc" if plan["routeType"] == "pcc" else ("ok" if plan["supported"] else "err")
                await ws.send_json({"type": "stage", "index": 2, "id": "attention",
                                    "status": att_st,
                                    "text": f"{plan['intent']} · confidence: {plan['confidence']:.2f}",
                                    "intent": plan["intent"], "confidence": plan["confidence"]})
                await asyncio.sleep(0.06)

                # Update session state based on intent
                if plan["intent"] == "MISSING_SLOT":
                    session_state["awaiting_slot"] = plan["params"]["slot"]
                else:
                    session_state["awaiting_slot"] = None

                if not plan["supported"]:
                    await ws.send_json({"type": "fail_from", "startIndex": 3, "reason": "No matched intent"})
                    continue

                # Stage 4: PRIVACY
                priv = privacy_check(plan, privacy)
                priv_st = ("pcc" if plan["routeType"] == "pcc" else "ok") if priv["approved"] else "err"
                await ws.send_json({"type": "stage", "index": 3, "id": "privacy",
                                    "status": priv_st, "text": priv["label"]})
                await asyncio.sleep(0.06)

                if not priv["approved"]:
                    await ws.send_json({"type": "fail_from", "startIndex": 4, "reason": priv["label"]})
                    continue

                # Stage 5: ROUTER
                route = route_check(plan, network)
                route_st = ("pcc" if route["routeType"] == "pcc" else "ok") if route["ok"] else "err"
                await ws.send_json({"type": "stage", "index": 4, "id": "router",
                                    "status": route_st, "text": route["label"]})
                await asyncio.sleep(0.06)

                if not route["ok"]:
                    await ws.send_json({"type": "fail_from", "startIndex": 5, "reason": route["label"]})
                    continue

                # Stage 6: MCP SERVER
                latency = random.randint(2, 8) + (len(route["servers"]) - 1) * random.randint(2, 4)
                mcp_st = "pcc" if route["routeType"] == "pcc" else "ok"
                await ws.send_json({"type": "stage", "index": 5, "id": "mcp",
                                    "status": mcp_st,
                                    "text": f"{' + '.join(route['servers'])} · {latency}ms",
                                    "servers": route["servers"]})
                await asyncio.sleep(0.04)

                # Stage 7: EXECUTION
                try:
                    result = execute(plan)
                except Exception as ex:
                    result = {"log": f"error · {str(ex)[:80]}", "entityId": f"err_{uid()}",
                              "response": f"Execution failed: {str(ex)[:100]}"}
                exec_st = "pcc" if route["routeType"] == "pcc" else "ok"
                await ws.send_json({"type": "stage", "index": 6, "id": "execution",
                                    "status": exec_st, "text": result["log"],
                                    "entityId": result["entityId"]})
                await asyncio.sleep(0.04)

                # Stage 8: RESPONSE
                resp_st = "pcc" if route["routeType"] == "pcc" else "ok"
                await ws.send_json({"type": "stage", "index": 7, "id": "response",
                                    "status": resp_st, "text": f"\u201c{result['response']}\u201d"})

                # TTS
                if tts:
                    speak(result["response"])

                # Save to memory
                conversation_history.append({
                    "turn": len(conversation_history) + 1,
                    "command": single_cmd,
                    "intent": plan["intent"],
                    "response": result["response"],
                    "timestamp": datetime.now().isoformat()
                })
                if len(conversation_history) > MAX_HISTORY:
                    conversation_history.pop(0)

                if is_chain and ci < len(commands) - 1:
                    await asyncio.sleep(0.3)

            await ws.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass


# ── REST ──────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "servers": len(SERVERS), "history": len(conversation_history)}

@app.get("/servers")
def get_servers():
    return SERVERS

@app.get("/history")
def get_history():
    return conversation_history[-10:]

@app.get("/")
def root():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("\n  🎙  Real Time Voice MCP — Backend Server")
    print("  ─────────────────────────────────────────")
    print(f"  → http://localhost:8000")
    print(f"  → WebSocket: ws://localhost:8000/ws")
    print(f"  → {len(SERVERS)} MCP servers registered")
    print(f"  → TTS enabled (macOS Samantha voice)")
    print("  → Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
