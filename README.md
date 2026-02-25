# Voice Agent Pipeline Demo

Single-file web app that visually simulates a voice-agent pipeline from wake-word detection through response delivery.

```
[INVOCATION] → [ASR] → [ATTENTION] → [PRIVACY GATE]
                                            ↓
[RESPONSE]   ← [EXECUTION] ← [MCP SERVER] ← [ROUTER]
```

Each stage lights up in real time as the request flows through the pipeline.
- **Green** = success
- **Red** = blocked or failed
- **Yellow** = PCC route taken
- **Blue** = currently active

## Features

- SVG pipeline diagram with animated connection lines and flowing particles
- Stage-by-stage log output with live updates
- MCP server registry with invocation highlighting
- Session state panel (ID, turns, entity, expiry countdown)
- Privacy mode and network mode toggles
- Four preset commands covering local, remote, PCC, and privacy-blocked flows
- Dark mode UI, mobile responsive, zero dependencies

## Fork and deploy in 2 minutes

1. **Fork** this repository on GitHub.
2. Go to **Settings > Pages** and set **Source** to **GitHub Actions**.
3. Push any commit to `main` (or the fork already triggered the workflow).
4. Open `https://<your-username>.github.io/<repo-name>/`.

No build step, no backend, no package install required. The included `.github/workflows/deploy.yml` handles everything.

## Run locally

```bash
git clone <your-fork-url>
cd <repo-name>
# Option 1: just open the file
open index.html

# Option 2: local server
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Add a new MCP server to the demo

All servers are defined in the `SERVERS` array inside `index.html`:

```js
const SERVERS = [
  { id: "com.apple.timer.mcp",     scope: "LOCAL",  needsNetwork: false },
  { id: "com.apple.calendar.mcp",  scope: "LOCAL",  needsNetwork: false },
  // ...
];
```

1. Add your server entry:
   ```js
   { id: "com.example.weather.mcp", scope: "REMOTE", needsNetwork: true }
   ```

2. Add a matching route in `classify()` so a command maps to the new server:
   ```js
   if (/weather|forecast/.test(t))
     return { supported: true, intent: "GET_WEATHER", confidence: 0.94, routeType: "remote",
              servers: ["com.example.weather.mcp"], privacyClass: "remote_data" };
   ```

3. Add execution output in `execute()`:
   ```js
   case "GET_WEATHER":
     return { log: "weather_req_01 · fetched", entityId: "weather_req_01",
              response: "It's 72°F and sunny" };
   ```

4. Optionally add a preset button in the HTML `presets` section.

## How the JS simulation maps to the C++ implementation

The JavaScript mirrors the C++ pipeline as a linear stage machine. Each JS function corresponds to a C++ pipeline stage:

| JS function | C++ equivalent | Purpose |
|---|---|---|
| `wakeScore()` | `InvocationDetector::score()` | Wake-word confidence scoring |
| `normalise()` | `ASREngine::transcribe()` | Utterance normalization |
| `classify()` | `AttentionClassifier::classify()` | Intent classification with confidence, route type, and server assignment |
| `privacyCheck()` | `PrivacyGate::evaluate()` | Privacy policy enforcement (blocks external search when privacy ON) |
| `routeCheck()` | `Router::resolve()` | Route validation (blocks remote when offline) |
| MCP dispatch | `MCPDispatcher::call()` | Server invocation with latency simulation |
| `execute()` | `Executor::run()` | Action execution and entity creation |
| Response stage | `ResponseBuilder::build()` | Final user-facing output |

Decision parity is centralized in three functions:
- **`classify()`** — sets intent, confidence, route type, server list, and privacy class
- **`privacyCheck()`** — enforces privacy-mode policy (e.g. block web search when privacy ON)
- **`routeCheck()`** — enforces connectivity policy (e.g. remote route blocked when OFFLINE)

If your C++ implementation changes policy or routing rules, update those three functions first so behavior stays aligned.

## GitHub Actions workflow

File: `.github/workflows/deploy.yml`

- Triggers on push to `main` and on manual `workflow_dispatch`
- Uploads the repository root as a Pages artifact
- Deploys with `actions/deploy-pages@v4`
- No build step or configuration needed
