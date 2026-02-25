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

# ── Regex Patterns ────────────────────────────────────────────────────
RE_TIMER_DURATION = re.compile(r'(\d+)\s*(minute|min|second|sec|hour|hr)')
RE_TIMER_NUMERIC = re.compile(r'^(\d+)$')
RE_REPEAT = re.compile(r'(do that again|repeat|again|redo)')
RE_HISTORY = re.compile(r'(what did i|last command|history|what was)')
RE_TIMER_KEYWORD = re.compile(r'timer|countdown|alarm')
RE_MUSIC_KEYWORD = re.compile(r'youtube|music|jazz|song|play|spotify')
RE_MUSIC_QUERY = re.compile(r'(play|on youtube music|on youtube|on spotify)')
RE_WEATHER_KEYWORD = re.compile(r'weather|temperature|forecast|rain|sunny')
RE_WEATHER_LOC = re.compile(r'(?:in|at|for)\s+(.+)')
RE_SCREENSHOT = re.compile(r'screenshot|screen\s*cap|capture\s*(the\s*)?screen|snap')
RE_CLIPBOARD = re.compile(r'clipboard|paste|what.*copied|copy that')
RE_SYSINFO = re.compile(r'battery|cpu|memory|ram|disk|system\s*info|storage')
RE_VOLUME_KEYWORD = re.compile(r'volume|mute|unmute|louder|quieter|sound')
RE_VOLUME_LEVEL = re.compile(r'(\d+)')
RE_VOLUME_MUTE = re.compile(r'mute')
RE_VOLUME_UNMUTE = re.compile(r'unmute')
RE_NOTE_KEYWORD = re.compile(r'(create|make|write|add)\s*(a\s*)?note')
RE_NOTE_BODY = re.compile(r'(create|make|write|add)\s*(a\s*)?note\s*(saying|that says|with)?\s*')
RE_REMINDER_KEYWORD = re.compile(r'remind|reminder')
RE_REMINDER_BODY = re.compile(r'(remind me to|set a reminder to|add a reminder to|remind me)\s*')
RE_FINDER_KEYWORD = re.compile(r'(open|show)\s*(the\s*)?(downloads?|documents?|desktop|home|finder|folder)')
RE_FINDER_FOLDER = re.compile(r'(downloads?|documents?|desktop|home|finder)')
RE_MESSAGE_KEYWORD = re.compile(r'message')
RE_FOLLOWUP_KEYWORD = re.compile(r'follow-up|follow up|meeting|calendar')
RE_SEARCH_KEYWORD = re.compile(r'search|google|look up')
RE_SEARCH_QUERY = re.compile(r'(search|the web|for|on google|on the internet|google|look up)')
RE_MAPS_KEYWORD = re.compile(r'map|direction|navigate|where is')
RE_MAPS_QUERY = re.compile(r'(open maps? to|show me|navigate to|directions? to|where is)')
RE_SEND_MSG = re.compile(r'send.*(message|text|imessage)')
RE_CREATE_EVENT = re.compile(r'(create|add|schedule|new).*(event|meeting|appointment)')
RE_OPEN_APP = re.compile(r'open\s+(\w+)')


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
        # Check if the user is answering with a duration
        m = RE_TIMER_DURATION.search(t)
        if m:
            dur = f"{m.group(1)} {m.group(2)}s"
            raw = int(m.group(1))
            unit = m.group(2)
            secs = raw * (3600 if 'hour' in unit or 'hr' in unit else 60 if 'min' in unit else 1)
            return {"supported": True, "intent": "SET_TIMER", "confidence": 0.98,
                    "routeType": "local", "servers": ["com.apple.timer.mcp"],
                    "privacyClass": "local_safe", "params": {"duration": dur, "seconds": secs}}
        # If they didn't provide a duration, but it's just a number:
        m2 = RE_TIMER_NUMERIC.search(t)
        if m2:
            dur = f"{m2.group(1)} minutes"
            secs = int(m2.group(1)) * 60
            return {"supported": True, "intent": "SET_TIMER", "confidence": 0.96,
                    "routeType": "local", "servers": ["com.apple.timer.mcp"],
                    "privacyClass": "local_safe", "params": {"duration": dur, "seconds": secs}}
        # If they entirely changed the subject, fall through to normal classification
        pass

    # Memory / context
    if RE_REPEAT.search(t):
        return {"supported": True, "intent": "REPEAT_LAST", "confidence": 0.95,
                "routeType": "local", "servers": ["com.apple.clipboard.mcp"],
                "privacyClass": "local_safe", "params": {}}

    if RE_HISTORY.search(t):
        return {"supported": True, "intent": "RECALL_HISTORY", "confidence": 0.93,
                "routeType": "local", "servers": ["com.apple.clipboard.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Timer
    if RE_TIMER_KEYWORD.search(t):
        m = RE_TIMER_DURATION.search(t)
        if m:
            dur = f"{m.group(1)} {m.group(2)}s"
            raw = int(m.group(1))
            unit = m.group(2)
            secs = raw * (3600 if 'hour' in unit or 'hr' in unit else 60 if 'min' in unit else 1)
            return {"supported": True, "intent": "SET_TIMER", "confidence": 0.96,
                    "routeType": "local", "servers": ["com.apple.timer.mcp"],
                    "privacyClass": "local_safe", "params": {"duration": dur, "seconds": secs}}
        else:
            # Missing duration
            return {"supported": True, "intent": "MISSING_SLOT", "confidence": 0.90,
                    "routeType": "local", "servers": [], "privacyClass": "local_safe",
                    "params": {"slot": "timer_duration", "message": "For how long?"}}

    # Music
    if RE_MUSIC_KEYWORD.search(t):
        query = RE_MUSIC_QUERY.sub('', t).strip()
        return {"supported": True, "intent": "PLAY_MUSIC", "confidence": 0.93,
                "routeType": "remote", "servers": ["com.google.youtubemusic"],
                "privacyClass": "remote_media", "params": {"query": query or "jazz"}}

    # Weather
    if RE_WEATHER_KEYWORD.search(t):
        m2 = RE_WEATHER_LOC.search(t)
        loc = m2.group(1).strip() if m2 else ""
        return {"supported": True, "intent": "GET_WEATHER", "confidence": 0.94,
                "routeType": "remote", "servers": ["com.apple.weather.mcp"],
                "privacyClass": "remote_data", "params": {"location": loc}}

    # Screenshot
    if RE_SCREENSHOT.search(t):
        return {"supported": True, "intent": "TAKE_SCREENSHOT", "confidence": 0.95,
                "routeType": "local", "servers": ["com.apple.screenshot.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Clipboard
    if RE_CLIPBOARD.search(t):
        return {"supported": True, "intent": "CLIPBOARD", "confidence": 0.92,
                "routeType": "local", "servers": ["com.apple.clipboard.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # System info
    if RE_SYSINFO.search(t):
        return {"supported": True, "intent": "SYSTEM_INFO", "confidence": 0.94,
                "routeType": "local", "servers": ["com.apple.systeminfo.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Volume
    if RE_VOLUME_KEYWORD.search(t):
        m3 = RE_VOLUME_LEVEL.search(t)
        level = int(m3.group(1)) if m3 else None
        mute = bool(RE_VOLUME_MUTE.search(t) and not RE_VOLUME_UNMUTE.search(t))
        unmute = bool(RE_VOLUME_UNMUTE.search(t))
        return {"supported": True, "intent": "VOLUME_CONTROL", "confidence": 0.93,
                "routeType": "local", "servers": ["com.apple.volume.mcp"],
                "privacyClass": "local_safe", "params": {"level": level, "mute": mute, "unmute": unmute}}

    # Notes
    if RE_NOTE_KEYWORD.search(t):
        body = RE_NOTE_BODY.sub('', t).strip()
        return {"supported": True, "intent": "CREATE_NOTE", "confidence": 0.91,
                "routeType": "local", "servers": ["com.apple.notes.mcp"],
                "privacyClass": "local_safe", "params": {"body": body or "New note from Voice MCP"}}

    # Reminders
    if RE_REMINDER_KEYWORD.search(t):
        body = RE_REMINDER_BODY.sub('', t).strip()
        return {"supported": True, "intent": "CREATE_REMINDER", "confidence": 0.92,
                "routeType": "local", "servers": ["com.apple.reminders.mcp"],
                "privacyClass": "local_safe", "params": {"body": body or "Voice MCP reminder"}}

    # Finder
    if RE_FINDER_KEYWORD.search(t):
        m4 = RE_FINDER_FOLDER.search(t)
        folder = m4.group(1) if m4 else "Finder"
        return {"supported": True, "intent": "OPEN_FINDER", "confidence": 0.93,
                "routeType": "local", "servers": ["com.apple.finder.mcp"],
                "privacyClass": "local_safe", "params": {"folder": folder}}

    # Messages + Calendar (cross-context)
    if RE_MESSAGE_KEYWORD.search(t) and RE_FOLLOWUP_KEYWORD.search(t):
        return {"supported": True, "intent": "FOLLOWUP_FROM_MESSAGE", "confidence": 0.91,
                "routeType": "pcc", "servers": ["com.apple.messages.mcp", "com.apple.calendar.mcp"],
                "privacyClass": "cross_context_local", "params": {}}

    # Web search
    if RE_SEARCH_KEYWORD.search(t):
        query = RE_SEARCH_QUERY.sub('', t).strip()
        return {"supported": True, "intent": "WEB_SEARCH", "confidence": 0.90,
                "routeType": "remote", "servers": ["com.apple.websearch.mcp"],
                "privacyClass": "external_search", "params": {"query": query or "search"}}

    # Maps
    if RE_MAPS_KEYWORD.search(t):
        query = RE_MAPS_QUERY.sub('', t).strip()
        return {"supported": True, "intent": "OPEN_MAPS", "confidence": 0.92,
                "routeType": "remote", "servers": ["com.apple.maps.mcp"],
                "privacyClass": "remote_data", "params": {"query": query or "current location"}}

    # Send message
    if RE_SEND_MSG.search(t):
        return {"supported": True, "intent": "SEND_MESSAGE", "confidence": 0.89,
                "routeType": "local", "servers": ["com.apple.messages.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Calendar event
    if RE_CREATE_EVENT.search(t):
        return {"supported": True, "intent": "CREATE_EVENT", "confidence": 0.90,
                "routeType": "local", "servers": ["com.apple.calendar.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Generic open app
    if RE_OPEN_APP.search(t):
        app_name = RE_OPEN_APP.search(t).group(1)
        return {"supported": True, "intent": "OPEN_APP", "confidence": 0.88,
                "routeType": "local", "servers": ["com.apple.finder.mcp"],
                "privacyClass": "local_safe", "params": {"app": app_name}}

    # Date & Time
    if re.search(r'\btime\b|date|day is it', t):
        return {"supported": True, "intent": "GET_DATE_TIME", "confidence": 0.96,
                "routeType": "local", "servers": ["com.apple.clock.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Calculator
    if re.search(r'calculate|math|plus|minus|times|divided', t):
        return {"supported": True, "intent": "CALCULATE", "confidence": 0.95,
                "routeType": "local", "servers": ["com.apple.calculator.mcp"],
                "privacyClass": "local_safe", "params": {"expression": t}}

    # Joke
    if re.search(r'joke|laugh', t):
        return {"supported": True, "intent": "TELL_JOKE", "confidence": 0.92,
                "routeType": "local", "servers": ["com.entertainment.jokes.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Quote
    if re.search(r'quote|inspire|wisdom|motivation', t):
        return {"supported": True, "intent": "GET_QUOTE", "confidence": 0.91,
                "routeType": "local", "servers": ["com.entertainment.quotes.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Coin Flip
    if re.search(r'flip.*coin|heads.*tails', t):
        return {"supported": True, "intent": "FLIP_COIN", "confidence": 0.94,
                "routeType": "local", "servers": ["com.tools.random.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Dice Roll
    if re.search(r'roll.*(die|dice)', t):
        return {"supported": True, "intent": "ROLL_DIE", "confidence": 0.94,
                "routeType": "local", "servers": ["com.tools.random.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Dictionary
    if re.search(r'define|meaning of|definition', t):
        word = re.sub(r'(define|meaning of|definition of|what is the)\s*', '', t).strip()
        return {"supported": True, "intent": "DEFINE_WORD", "confidence": 0.92,
                "routeType": "remote", "servers": ["com.reference.dictionary.mcp"],
                "privacyClass": "external_search", "params": {"word": word}}

    # Currency
    if re.search(r'convert.*(currency|usd|eur|gbp|yen)|price of', t):
        return {"supported": True, "intent": "CONVERT_CURRENCY", "confidence": 0.90,
                "routeType": "remote", "servers": ["com.finance.currency.mcp"],
                "privacyClass": "external_search", "params": {"query": t}}

    # Local IP
    if re.search(r'my ip|ip address', t):
        return {"supported": True, "intent": "GET_IP", "confidence": 0.95,
                "routeType": "local", "servers": ["com.network.ip.mcp"],
                "privacyClass": "local_safe", "params": {}}

    # Uptime
    if re.search(r'uptime|how long.*running', t):
        return {"supported": True, "intent": "GET_UPTIME", "confidence": 0.93,
                "routeType": "local", "servers": ["com.system.uptime.mcp"],
                "privacyClass": "local_safe", "params": {}}

    return {"supported": False, "intent": "UNSUPPORTED", "confidence": 0.58,
            "routeType": "none", "servers": [], "privacyClass": "unknown", "params": {}}


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
async def execute(plan: dict) -> dict:
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

        async def timer_task(s):
            await asyncio.sleep(s)
            try:
                cmd = ['osascript', '-e', 'display notification "⏱ Timer done!" with title "Voice MCP" sound name "Glass"']
                # Use async subprocess to avoid blocking the loop
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await proc.wait()
            except Exception as e:
                print(f"Timer notification failed: {e}")

        asyncio.create_task(timer_task(secs))
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
                    result = await execute(plan)
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

app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    print("\n  🎙  Real Time Voice MCP — Backend Server")
    print("  ─────────────────────────────────────────")
    print(f"  → http://localhost:8000")
    print(f"  → WebSocket: ws://localhost:8000/ws")
    print(f"  → {len(SERVERS)} MCP servers registered")
    print(f"  → TTS enabled (macOS Samantha voice)")
    print("  → Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
