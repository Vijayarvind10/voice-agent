#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# Voice Agent — Automated Bug-Regression Test Runner
# Runs every 5 minutes. Validates HTML structure, JS correctness,
# pipeline logic, and known bug-fix regressions.
# Usage:  chmod +x test_runner.sh && ./test_runner.sh
# ──────────────────────────────────────────────────────────────
set -eu

FILE="$(cd "$(dirname "$0")" && pwd)/index.html"
INTERVAL=300  # seconds (5 minutes)
PASS=0
FAIL=0
RUN=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()  { printf "${CYAN}[TEST]${NC} %s\n" "$*"; }
pass() { PASS=$((PASS+1)); printf "  ${GREEN}✓${NC} %s\n" "$*"; }
fail() { FAIL=$((FAIL+1)); printf "  ${RED}✗${NC} %s\n" "$*"; }
warn() { printf "  ${YELLOW}⚠${NC} %s\n" "$*"; }
header() { printf "\n${BOLD}━━━ %s ━━━${NC}\n" "$*"; }

run_tests() {
  RUN=$((RUN+1))
  PASS=0
  FAIL=0
  CONTENT=$(cat "$FILE")

  header "Run #$RUN — $(date '+%Y-%m-%d %H:%M:%S')"

  # ─── 1. File existence & basic HTML structure ───
  log "Structural checks"

  if [ -f "$FILE" ]; then
    pass "index.html exists"
  else
    fail "index.html not found at $FILE"
    return
  fi

  if echo "$CONTENT" | grep -q '<!doctype html>'; then
    pass "Has DOCTYPE"
  else
    fail "Missing DOCTYPE"
  fi

  if echo "$CONTENT" | grep -q '<html lang="en">'; then
    pass "Has lang attribute"
  else
    fail "Missing lang attribute on <html>"
  fi

  if echo "$CONTENT" | grep -q '<meta name="description"'; then
    pass "Has meta description (SEO)"
  else
    fail "Missing meta description"
  fi

  # ─── 2. Bug 1 regression: SVG class handling ───
  log "Bug 1 — SVG class handling"

  if echo "$CONTENT" | grep -q "className.baseVal"; then
    fail "Bug 1 REGRESSION: className.baseVal still present (should use setAttribute)"
  else
    pass "No className.baseVal usage — setAttribute used instead"
  fi

  if echo "$CONTENT" | grep -q "setAttribute('class', 'conn-line')"; then
    pass "conn-line reset uses setAttribute"
  else
    fail "conn-line reset not using setAttribute"
  fi

  if echo "$CONTENT" | grep -q "setAttribute('class', 'conn-arrow')"; then
    pass "conn-arrow reset uses setAttribute"
  else
    fail "conn-arrow reset not using setAttribute"
  fi

  # ─── 3. Bug 2 regression: Session expiry & live dot ───
  log "Bug 2 — Session expiry logic"

  if echo "$CONTENT" | grep -q "if (session.active) dom.liveDot.classList.remove"; then
    pass "done() conditionally sets live dot based on session.active"
  else
    fail "Bug 2 REGRESSION: done() unconditionally removes 'off' from liveDot"
  fi

  if echo "$CONTENT" | grep -q "if (!session.active) session.id = uid()"; then
    pass "Session ID regenerated on expired session"
  else
    fail "Bug 2 REGRESSION: Session ID not regenerated on expiry"
  fi

  # ─── 4. Bug 3 regression: Pipeline cancellation ───
  log "Bug 3 — Pipeline cancellation"

  if echo "$CONTENT" | grep -q "if (running)"; then
    # Check it's NOT just 'if (running) return;'
    if echo "$CONTENT" | grep -q "if (running) return;"; then
      fail "Bug 3 REGRESSION: Pipeline still blocks new commands with 'if (running) return'"
    else
      pass "Pipeline allows cancellation of in-flight runs"
    fi
  else
    fail "Bug 3 REGRESSION: No running guard found"
  fi

  # ─── 5. Bug 4 regression: normalise() casing ───
  log "Bug 4 — Transcript normalisation"

  if echo "$CONTENT" | grep -q 'c\[0\]\.toLowerCase()'; then
    fail "Bug 4 REGRESSION: normalise() still lowercases first character"
  else
    pass "normalise() preserves original casing"
  fi

  # ─── 6. Bug 7 regression: XSS single-quote escape ───
  log "Bug 7 — XSS protection"

  if echo "$CONTENT" | grep -q "&#39;"; then
    pass "esc() escapes single quotes (&#39;)"
  else
    fail "Bug 7 REGRESSION: esc() does not escape single quotes"
  fi

  if echo "$CONTENT" | grep -q '&amp;' && echo "$CONTENT" | grep -q '&lt;' && echo "$CONTENT" | grep -q '&gt;' && echo "$CONTENT" | grep -q '&quot;'; then
    pass "esc() handles all standard HTML entities"
  else
    fail "esc() missing standard HTML entity escapes"
  fi

  # ─── 7. Bug 8 regression: AudioContext leak guard ───
  log "Bug 8 — AudioContext leak prevention"

  if echo "$CONTENT" | grep -q "pendingMicPromise"; then
    pass "Mic promise tracking variable exists"
  else
    fail "Bug 8 REGRESSION: No pendingMicPromise guard"
  fi

  if echo "$CONTENT" | grep -q "pendingMicPromise !== micPromiseId"; then
    pass "getUserMedia promise cancellation check present"
  else
    fail "Bug 8 REGRESSION: No promise cancellation check"
  fi

  if echo "$CONTENT" | grep -q "pendingMicPromise = null"; then
    pass "stopAudioVis invalidates pending promise"
  else
    fail "Bug 8 REGRESSION: stopAudioVis doesn't invalidate promise"
  fi

  # ─── 8. Bug 9 regression: aria-checked sync ───
  log "Bug 9 — aria-checked sync on presets"

  ARIA_PRIVACY=$(echo "$CONTENT" | grep -c "privacyToggle.setAttribute('aria-checked'" || true)
  ARIA_NETWORK=$(echo "$CONTENT" | grep -c "networkToggle.setAttribute('aria-checked'" || true)

  if [ "$ARIA_PRIVACY" -ge 2 ]; then
    pass "Privacy toggle aria-checked set in both click handler and preset handler"
  else
    fail "Bug 9 REGRESSION: Privacy toggle aria-checked not synced in preset handler (found $ARIA_PRIVACY occurrences)"
  fi

  if [ "$ARIA_NETWORK" -ge 2 ]; then
    pass "Network toggle aria-checked set in both click handler and preset handler"
  else
    fail "Bug 9 REGRESSION: Network toggle aria-checked not synced in preset handler (found $ARIA_NETWORK occurrences)"
  fi

  # ─── 9. Bug 10 regression: Responsive visualizer ───
  log "Bug 10 — Responsive canvas sizing"

  if echo "$CONTENT" | grep -q '#micVisualizer' && echo "$CONTENT" | grep -q 'width: 100%' && echo "$CONTENT" | grep -q 'height: 100%'; then
    pass "Visualizer canvas uses percentage-based sizing"
  else
    fail "Bug 10 REGRESSION: Visualizer canvas still uses hardcoded px sizing"
  fi

  if echo "$CONTENT" | grep -q "dom.micVis.width"; then
    pass "drawVis() reads canvas dimensions dynamically"
  else
    fail "Bug 10 REGRESSION: drawVis() uses hardcoded dimensions"
  fi

  # ─── 10. General code quality checks ───
  log "General quality checks"

  if echo "$CONTENT" | grep -q 'aria-label="Microphone"'; then
    pass "Mic button has aria-label"
  else
    fail "Mic button missing aria-label"
  fi

  if echo "$CONTENT" | grep -q 'role="switch"'; then
    pass "Toggle buttons have role=switch"
  else
    fail "Toggle buttons missing role=switch"
  fi

  if echo "$CONTENT" | grep -q 'aria-live="polite"'; then
    pass "Log panel has aria-live for screen readers"
  else
    fail "Log panel missing aria-live"
  fi

  if echo "$CONTENT" | grep -q '<label.*for="commandInput"'; then
    pass "Input has associated label"
  else
    fail "Input missing associated label"
  fi

  SCRIPT_TAGS=$(echo "$CONTENT" | grep -c '<script' || true)
  if [ "$SCRIPT_TAGS" -eq 1 ]; then
    pass "Single script block (no external script injection)"
  else
    warn "Found $SCRIPT_TAGS script tags — verify no unexpected injections"
  fi

  # ─── Summary ───
  TOTAL=$((PASS+FAIL))
  header "Results: $PASS/$TOTAL passed, $FAIL failed"

  if [ "$FAIL" -eq 0 ]; then
    printf "${GREEN}${BOLD}All tests passed! ✓${NC}\n"
  else
    printf "${RED}${BOLD}$FAIL test(s) failed — review above for details${NC}\n"
  fi
}

# ─── Main loop ───
printf "${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${NC}\n"
printf "${BOLD}${CYAN}║  Voice Agent — Automated Test Runner             ║${NC}\n"
printf "${BOLD}${CYAN}║  Interval: every %d seconds (%d min)              ║${NC}\n" "$INTERVAL" $((INTERVAL/60))
printf "${BOLD}${CYAN}║  Target:   %s   ║${NC}\n" "$(basename "$FILE")"
printf "${BOLD}${CYAN}║  Press Ctrl+C to stop                            ║${NC}\n"
printf "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${NC}\n"

# Run immediately, then every INTERVAL seconds
while true; do
  run_tests
  printf "\n${YELLOW}Next run in %d minutes... (Ctrl+C to stop)${NC}\n" $((INTERVAL/60))
  sleep "$INTERVAL"
done
