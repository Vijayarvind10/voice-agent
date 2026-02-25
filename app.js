(function () {
  /* ── Boot sequence ─── */
  const boot = document.getElementById('bootOverlay');
  const canvas = document.getElementById('starCanvas');
  const appShell = document.getElementById('appShell');
  setTimeout(() => { boot.classList.add('fade-out'); canvas.classList.add('visible'); appShell.classList.add('revealed'); }, 1500);
  setTimeout(() => boot.remove(), 2200);

  /* ── Glow Effect ─── */
  function initGlow() {
    document.querySelectorAll('.glow-surface, .card').forEach(el => {
      el.addEventListener('mousemove', e => {
        const rect = el.getBoundingClientRect();
        el.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
        el.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
      });
    });
  }
  initGlow();

  /* ── Scroll Animations (IntersectionObserver & Parallax) ─── */
  const observerPairs = document.querySelectorAll('.reveal, .zoom-in, .fade-up');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  observerPairs.forEach(el => observer.observe(el));

  const auroraBg = document.querySelector('.aurora');
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    auroraBg.style.transform = `translateY(${scrolled * 0.3}px)`;
  });

  /* ── Star field ─── */
  const sCtx = canvas.getContext('2d');
  let stars = [];
  function initStars() {
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    stars = Array.from({ length: 120 }, () => ({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      r: Math.random() * 1.2 + 0.3, a: Math.random(), s: Math.random() * 0.003 + 0.001
    }));
  }
  function drawStars() {
    sCtx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach(s => {
      s.a += s.s; if (s.a > 1) s.s = -Math.abs(s.s); if (s.a < 0.1) s.s = Math.abs(s.s);
      sCtx.beginPath(); sCtx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      sCtx.fillStyle = `rgba(255,255,255,${s.a * 0.4})`; sCtx.fill();
    });
    requestAnimationFrame(drawStars);
  }
  initStars(); drawStars();
  window.addEventListener('resize', initStars);

  /* ── Constants ─── */
  const STAGE_IDS = ["invocation", "asr", "attention", "privacy", "router", "mcp", "execution", "response"];
  const STAGE_LABELS = { invocation: "INVOCATION", asr: "ASR", attention: "ATTENTION", privacy: "PRIVACY", router: "ROUTER", mcp: "MCP", execution: "EXECUTION", response: "RESPONSE" };
  const CONN_BEFORE_STAGE = { 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6 };
  const SERVERS = [
    { id: "com.apple.timer.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" },
    { id: "com.apple.calendar.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--blue)" },
    { id: "com.apple.messages.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--purple)" },
    { id: "com.apple.notes.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" },
    { id: "com.apple.reminders.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--blue)" },
    { id: "com.apple.volume.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--purple)" },
    { id: "com.apple.finder.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--yellow)" },
    { id: "com.apple.screenshot.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" },
    { id: "com.apple.clipboard.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--blue)" },
    { id: "com.apple.systeminfo.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--purple)" },
    { id: "com.google.youtubemusic", scope: "REMOTE", needsNetwork: true, color: "var(--red)" },
    { id: "com.apple.maps.mcp", scope: "REMOTE", needsNetwork: true, color: "var(--yellow)" },
    { id: "com.apple.weather.mcp", scope: "REMOTE", needsNetwork: true, color: "var(--blue)" },
    { id: "com.apple.websearch.mcp", scope: "REMOTE", needsNetwork: true, color: "var(--red)" },
    { id: "com.apple.clock.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" },
    { id: "com.apple.calculator.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--blue)" },
    { id: "com.entertainment.jokes.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--purple)" },
    { id: "com.entertainment.quotes.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--yellow)" },
    { id: "com.tools.random.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" },
    { id: "com.reference.dictionary.mcp", scope: "REMOTE", needsNetwork: true, color: "var(--blue)" },
    { id: "com.finance.currency.mcp", scope: "REMOTE", needsNetwork: true, color: "var(--yellow)" },
    { id: "com.network.ip.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--purple)" },
    { id: "com.system.uptime.mcp", scope: "LOCAL", needsNetwork: false, color: "var(--green)" }
  ];

  /* ── DOM ─── */
  const $ = s => document.querySelector(s);
  const dom = {
    input: $('#commandInput'), speak: $('#speakBtn'), logs: $('#logPanel'),
    presets: $('#presetGrid'), serverList: $('#serverList'),
    sId: $('#session-id'), sActive: $('#session-active'), sTurns: $('#session-turns'),
    sEntity: $('#session-entity'), sExpiry: $('#session-expiry'),
    micBtn: $('#micBtn'), micLabel: $('#micLabel'), micVis: $('#micVisualizer'),
    intentBadge: $('#intentBadge'), intentText: $('#intentText'), confArc: $('#confArc'),
    privacyToggle: $('#privacyToggle'), networkToggle: $('#networkToggle'), ttsToggle: $('#ttsToggle'),
    liveDot: $('#liveDot'), liveLabel: $('#liveLabel'), stageCount: $('#stageCount'),
    idProgress: $('#idProgress'),
    stages: {}, conns: [], arrows: [], particles: []
  };
  STAGE_IDS.forEach(id => dom.stages[id] = document.getElementById('stage-' + id));
  for (let i = 0; i <= 6; i++) { dom.conns[i] = $('#conn-' + i); dom.arrows[i] = $('#arrow-' + i); dom.particles[i] = $('#particle-' + i); }

  /* ── Toggle logic ─── */
  function getPrivacy() { return dom.privacyToggle.classList.contains('on') ? 'ON' : 'OFF'; }
  function getNetwork() { return dom.networkToggle.classList.contains('on') ? 'ONLINE' : 'OFFLINE'; }
  dom.privacyToggle.addEventListener('click', () => { dom.privacyToggle.classList.toggle('on'); dom.privacyToggle.setAttribute('aria-checked', dom.privacyToggle.classList.contains('on')); renderServers(); });
  dom.networkToggle.addEventListener('click', () => { dom.networkToggle.classList.toggle('on'); dom.networkToggle.setAttribute('aria-checked', dom.networkToggle.classList.contains('on')); renderServers(); });
  dom.ttsToggle.addEventListener('click', () => { dom.ttsToggle.classList.toggle('on'); dom.ttsToggle.setAttribute('aria-checked', dom.ttsToggle.classList.contains('on')); });
  function getTTS() { return dom.ttsToggle.classList.contains('on'); }

  /* ── Session ─── */
  const session = { id: uid(), turns: 0, lastEntity: "none", expiresIn: 95, active: true };
  let running = false, runCounter = 0, completedStages = 0, pendingMicPromise = null;
  let pipelineStartTime = 0, currentRunMeta = null;

  // Multi-turn context
  let dialogState = { awaiting_slot: null };

  /* ── Web Speech API ─── */
  let recognition = null, audioCtx = null, analyser = null, micStream = null;
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRec) {
    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
  }
  let classifyDebounce = null;
  let micListening = false;

  dom.micBtn.addEventListener('click', () => {
    if (!recognition) { dom.micLabel.textContent = 'Speech API not supported'; return; }
    if (micListening) { recognition.stop(); return; }
    micListening = true;
    dom.micBtn.classList.add('listening');
    dom.micLabel.textContent = 'Listening...';
    dom.input.value = '';
    dom.input.classList.add('interim');
    // startAudioVis() moved to recognition.onstart to prevent mic conflict
    if (recognition) recognition._bargeInSent = false;
    try {
      recognition.start();
    } catch (e) {
      console.error("SpeechRecognition start failed:", e);
      micListening = false;
      dom.micBtn.classList.remove('listening');
      dom.micLabel.textContent = 'Error starting mic';
    }
  });

  if (recognition) {
    recognition.onresult = (e) => {
      // Send barge-in signal to backend as soon as speech is detected
      if (wsConnected && ws && ws.readyState === 1 && !micListening) {
        // we already sent it, or maybe this is a good place to be safe.
      }
      // We can better send barge_in immediately
      if (wsConnected && ws && ws.readyState === 1) {
        // Only send once per listening session to avoid spamming
        if (!recognition._bargeInSent) {
          ws.send(JSON.stringify({ type: "barge_in" }));
          recognition._bargeInSent = true;
        }
      }

      let interim = '', final = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }
      if (final) {
        dom.input.value = final;
        dom.input.classList.remove('interim');
        updateIntentBadge(final);
      } else if (interim) {
        dom.input.value = interim;
        dom.input.classList.add('interim');
        clearTimeout(classifyDebounce);
        classifyDebounce = setTimeout(() => {
          updateIntentBadge(interim);

          // SOA Feature: Low-Latency Predictive Execution
          // If we match an intent with high confidence and it's not missing slots, trigger early
          const plan = classify(normalise(interim));
          if (plan.supported && plan.intent !== 'MISSING_SLOT' && plan.confidence >= 0.94) {
            recognition.stop(); // Force early completion
          }
        }, 200);
      }
    };
    recognition.onend = () => {
      micListening = false;
      dom.micBtn.classList.remove('listening', 'processing');
      dom.micLabel.textContent = 'Tap to speak';
      stopAudioVis();
      const val = dom.input.value.trim();
      if (val && !running) {
        dom.micBtn.classList.add('processing');
        dom.micLabel.textContent = 'Processing...';
        setTimeout(() => { dom.micBtn.classList.remove('processing'); dom.micLabel.textContent = 'Tap to speak'; }, 600);
        runPipeline(val);
      }
    };
    recognition.onstart = () => {
      micListening = true;
      dom.micBtn.classList.add('listening');
      dom.micLabel.textContent = 'Listening...';
      // Start visualizer only after recognition has successfully started (avoids mic conflict)
      startAudioVis();
    };
    recognition.onerror = (e) => {
      micListening = false;
      dom.micBtn.classList.remove('listening', 'processing');
      if (e.error !== 'no-speech') dom.micLabel.textContent = 'Mic error — try again';
      else dom.micLabel.textContent = 'No speech detected';
      stopAudioVis();
    };
  }

  /* ── Audio visualizer ─── */
  const visCtx = dom.micVis.getContext('2d');
  let visRAF = null;
  function startAudioVis() {
    // Bug 8 fix: track pending promise to prevent AudioContext leaks
    const micPromiseId = {};
    pendingMicPromise = micPromiseId;
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      // If mic was toggled off before promise resolved, clean up immediately
      if (pendingMicPromise !== micPromiseId) {
        stream.getTracks().forEach(t => t.stop());
        return;
      }
      micStream = stream;
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      audioCtx.createMediaStreamSource(stream).connect(analyser);
      drawVis();
    }).catch(() => { });
  }
  function drawVis() {
    if (!analyser) return;
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    const w = dom.micVis.width, h = dom.micVis.height, cx = w / 2, cy = h / 2;
    visCtx.clearRect(0, 0, w, h);
    const bars = 24, step = (Math.PI * 2) / bars;
    for (let i = 0; i < bars; i++) {
      const val = (data[i % data.length] || 0) / 255;
      const len = 6 + val * 14;
      const angle = i * step - Math.PI / 2;
      const r1 = Math.min(w, h) * 0.3, r2 = r1 + len;
      visCtx.beginPath();
      visCtx.moveTo(cx + Math.cos(angle) * r1, cy + Math.sin(angle) * r1);
      visCtx.lineTo(cx + Math.cos(angle) * r2, cy + Math.sin(angle) * r2);
      visCtx.strokeStyle = `rgba(10,132,255,${0.4 + val * 0.6})`;
      visCtx.lineWidth = 2; visCtx.lineCap = 'round'; visCtx.stroke();
    }
    visRAF = requestAnimationFrame(drawVis);
  }
  function stopAudioVis() {
    pendingMicPromise = null; // Bug 8 fix: invalidate pending promise
    if (visRAF) cancelAnimationFrame(visRAF);
    const w = dom.micVis.width, h = dom.micVis.height;
    visCtx.clearRect(0, 0, w, h);
    if (micStream) micStream.getTracks().forEach(t => t.stop());
    if (audioCtx) audioCtx.close().catch(() => { });
    audioCtx = null; analyser = null; micStream = null;
  }

  /* ── Intent badge ─── */
  function updateIntentBadge(text) {
    const plan = classify(normalise(text));
    dom.intentText.textContent = plan.intent + ' · ' + (plan.confidence * 100).toFixed(0) + '%';
    const circumference = 94.25;
    dom.confArc.setAttribute('stroke-dashoffset', circumference * (1 - plan.confidence));
    const color = plan.supported ? (plan.routeType === 'pcc' ? 'var(--yellow)' : 'var(--blue)') : 'var(--red)';
    dom.confArc.setAttribute('stroke', color);
  }

  /* ── WebSocket connection ─── */
  let ws = null, wsConnected = false;
  function connectWS() {
    try {
      ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => { wsConnected = true; dom.micLabel.textContent = '● Server connected — tap to speak'; };
      ws.onclose = () => { wsConnected = false; dom.micLabel.textContent = 'Tap to speak (offline mode)'; setTimeout(connectWS, 3000); };
      ws.onerror = () => { wsConnected = false; };
      ws.onmessage = (e) => { handleWSMessage(JSON.parse(e.data)); };
    } catch (_) { wsConnected = false; setTimeout(connectWS, 3000); }
  }
  connectWS();

  let wsResolve = null;
  function handleWSMessage(msg) {
    if (msg.type === 'servers') {
      if (msg.servers && msg.servers.length) {
        SERVERS.length = 0;
        const srvColors = {
          'timer': 'var(--green)', 'calendar': 'var(--blue)', 'messages': 'var(--purple)',
          'notes': 'var(--green)', 'reminders': 'var(--blue)', 'volume': 'var(--purple)', 'finder': 'var(--yellow)',
          'screenshot': 'var(--green)', 'clipboard': 'var(--blue)', 'systeminfo': 'var(--purple)',
          'youtubemusic': 'var(--red)', 'maps': 'var(--yellow)', 'weather': 'var(--blue)', 'websearch': 'var(--red)',
          'clock': 'var(--green)', 'calculator': 'var(--blue)', 'jokes': 'var(--purple)', 'quotes': 'var(--yellow)',
          'random': 'var(--green)', 'dictionary': 'var(--blue)', 'currency': 'var(--yellow)', 'ip': 'var(--purple)',
          'uptime': 'var(--green)'
        };
        msg.servers.forEach(s => {
          const key = s.id.split('.').slice(-1)[0].replace('.mcp', '');
          SERVERS.push({ id: s.id, scope: s.scope, needsNetwork: s.needsNetwork, color: srvColors[key] || 'var(--blue)' });
        });
        renderServers();
      }
    } else if (msg.type === 'stage') {
      const idx = msg.index, id = msg.id, status = msg.status, text = msg.text;
      // Capture analytics metadata from WS stages
      if (idx === 2 && currentRunMeta) {
        currentRunMeta.intent = msg.intent || 'UNKNOWN';
        currentRunMeta.confidence = msg.confidence || 0;
      }
      if (idx === 4 && currentRunMeta) {
        currentRunMeta.routeType = text.toLowerCase().includes('local') ? 'local' : text.toLowerCase().includes('pcc') ? 'pcc' : 'remote';
      }
      if (idx === 7 && currentRunMeta && status !== 'err') {
        currentRunMeta.succeeded = true;
      }
      const connIdx = CONN_BEFORE_STAGE[idx];
      if (connIdx !== undefined) { litConn(connIdx, 'active'); animateParticle(connIdx); }
      setTimeout(() => {
        setStage(id, 'active'); updateProgress(idx);
        setTimeout(() => {
          const el = dom.stages[id];
          if (el) { el.style.animation = 'stagePopIn 0.3s var(--spring)'; setTimeout(() => el.style.animation = '', 300); }
          setStage(id, statusClass(status));
          if (connIdx !== undefined) litConn(connIdx, status);
          addLog(STAGE_LABELS[id], text, status, true);
          completedStages = idx + 1;
          dom.stageCount.textContent = completedStages + ' / 8 stages';
          if (msg.entityId) { session.lastEntity = msg.entityId; renderSession(); }
          // Flash server rows
          if (msg.servers) {
            msg.servers.forEach(sid => {
              const row = dom.serverList.querySelector('[data-sid="' + sid + '"]');
              if (row) { row.classList.add('hit'); setTimeout(() => row.classList.remove('hit'), 900); }
            });
          }
        }, 120);
      }, 60);
    } else if (msg.type === 'fail_from') {
      const remaining = STAGE_IDS.slice(msg.startIndex);
      remaining.forEach((sid, i) => {
        setTimeout(() => {
          const gi = msg.startIndex + i;
          const ci = CONN_BEFORE_STAGE[gi];
          if (ci !== undefined) litConn(ci, 'err');
          setStage(sid, 'error'); updateProgress(gi, 'error');
          const txt = i === remaining.length - 1 ? '\u201c' + msg.reason + '\u201d' : 'skipped';
          addLog(STAGE_LABELS[sid], txt, 'err', true);
        }, i * 60);
      });
      setTimeout(() => done(), remaining.length * 60 + 100);
    } else if (msg.type === 'done') {
      done();
    }
  }

  /* ── Init ─── */
  renderSession(); renderServers(); resetAll();
  setInterval(() => {
    if (session.expiresIn > 0) session.expiresIn--;
    session.active = session.expiresIn > 0;
    renderSession();
  }, 1000);

  /* ── Events ─── */
  dom.speak.addEventListener('click', () => runPipeline(dom.input.value));
  dom.input.addEventListener('keydown', e => { if (e.key === 'Enter') runPipeline(dom.input.value); });
  dom.input.addEventListener('input', () => { updateIntentBadge(dom.input.value); });
  dom.presets.addEventListener('click', e => {
    const btn = e.target.closest('button[data-command]');
    if (!btn) return;
    dom.input.value = btn.dataset.command;
    dom.input.classList.remove('interim');
    // Bug 9 fix: sync aria-checked when presets change toggle state
    if (btn.dataset.privacy === 'ON') dom.privacyToggle.classList.add('on'); else dom.privacyToggle.classList.remove('on');
    dom.privacyToggle.setAttribute('aria-checked', btn.dataset.privacy === 'ON');
    if (btn.dataset.network === 'ONLINE') dom.networkToggle.classList.add('on'); else dom.networkToggle.classList.remove('on');
    dom.networkToggle.setAttribute('aria-checked', btn.dataset.network === 'ONLINE');
    renderServers();
    updateIntentBadge(btn.dataset.command);
    runPipeline(btn.dataset.command);
  });

  /* ── Pipeline runner ─── */
  async function runPipeline(raw) {
    // Bug 3 fix: allow cancellation — new command cancels in-flight pipeline
    const cmd = (raw || '').trim();
    if (!cmd) { if (!running) addLog('SYSTEM', 'Enter a command first.', 'err', true); return; }
    if (running) {
      runCounter++; // cancel the in-flight run
      await sleep(200); // let the old run exit
      running = false;
    }
    // UX: Loading state
    dom.speak.innerHTML = '<svg class="spinner-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="10" stroke-opacity="0.2"></circle><path d="M12 2a10 10 0 0 1 10 10" stroke-opacity="1"></path></svg> Running...';
    dom.speak.classList.add('processing');

    running = true; setDisabled(true); runCounter++; completedStages = 0;
    pipelineStartTime = performance.now();
    currentRunMeta = { cmd, intent: 'UNKNOWN', confidence: 0, routeType: 'none', succeeded: false };
    const rid = runCounter;
    resetAll(); clearLogs();
    // Bug 2 fix: regenerate session ID if session had expired
    if (!session.active) session.id = uid();
    session.turns++; session.expiresIn = 95; session.active = true;
    renderSession(); updateProgress(-1);
    dom.liveDot.classList.remove('off');
    addLog('SYSTEM', 'Turn ' + session.turns + ' started.', 'ok', false);
    updateIntentBadge(cmd);

    // Use backend if connected
    if (wsConnected && ws && ws.readyState === 1) {
      addLog('SYSTEM', 'Backend connected — executing real actions', 'ok', false);
      ws.send(JSON.stringify({ command: cmd, privacy: getPrivacy(), network: getNetwork(), tts: getTTS() }));
      return; // stages arrive async via handleWSMessage
    }

    // Fallback: local simulation
    addLog('SYSTEM', 'Offline mode — simulating pipeline', 'pcc', false);
    const env = { privacyMode: getPrivacy(), networkMode: getNetwork() };
    if (!await stage(0, 'invocation', 'ok', 'confidence: ' + wakeScore(cmd).toFixed(2) + ' → WAKE', rid)) return done();
    const transcript = normalise(cmd);
    if (!await stage(1, 'asr', 'ok', '\u201c' + transcript + '\u201d', rid)) return done();
    const plan = classify(transcript);
    const attSt = plan.routeType === 'pcc' ? 'pcc' : plan.supported ? 'ok' : 'err';
    if (!await stage(2, 'attention', attSt, plan.intent + ' · confidence: ' + plan.confidence.toFixed(2), rid)) return done();
    currentRunMeta.intent = plan.intent;
    currentRunMeta.confidence = plan.confidence;
    currentRunMeta.routeType = plan.routeType;

    // Update dialog state for multi-turn
    if (plan.intent === 'MISSING_SLOT') dialogState.awaiting_slot = plan.params.slot;
    else dialogState.awaiting_slot = null;

    if (!plan.supported) { await failFrom(3, rid, 'No matched intent.'); return done(); }
    const priv = privacyCheck(plan, env);
    const privSt = priv.approved ? (plan.routeType === 'pcc' ? 'pcc' : 'ok') : 'err';
    if (!await stage(3, 'privacy', privSt, priv.label, rid)) return done();
    if (!priv.approved) { await failFrom(4, rid, priv.label); return done(); }
    const route = routeCheck(plan, env);
    const routeSt = route.ok ? (route.routeType === 'pcc' ? 'pcc' : 'ok') : 'err';
    if (!await stage(4, 'router', routeSt, route.label, rid)) return done();
    if (!route.ok) { await failFrom(5, rid, route.label); return done(); }
    const latency = randInt(2, 6) + (route.servers.length - 1) * randInt(2, 4);
    for (const sid of route.servers) {
      const row = dom.serverList.querySelector('[data-sid="' + sid + '"]');
      if (row) { row.classList.add('hit'); setTimeout(() => row.classList.remove('hit'), 900); }
      await sleep(100);
    }
    const mcpSt = route.routeType === 'pcc' ? 'pcc' : 'ok';
    if (!await stage(5, 'mcp', mcpSt, route.servers.join(' + ') + ' · ' + latency + 'ms', rid)) return done();
    const exec = execute(plan);
    const execSt = route.routeType === 'pcc' ? 'pcc' : 'ok';
    if (!await stage(6, 'execution', execSt, exec.log, rid)) return done();
    session.lastEntity = exec.entityId; renderSession();
    const respSt = route.routeType === 'pcc' ? 'pcc' : 'ok';
    await stage(7, 'response', respSt, '\u201c' + exec.response + '\u201d', rid);
    currentRunMeta.succeeded = true;
    done();
  }

  /* ── Stage animation ─── */
  async function stage(idx, id, status, text, rid) {
    if (runCounter !== rid) return false;
    const connIdx = CONN_BEFORE_STAGE[idx];
    if (connIdx !== undefined) { litConn(connIdx, 'active'); animateParticle(connIdx); await sleep(80); }
    setStage(id, 'active'); updateProgress(idx);
    await sleep(150);
    if (runCounter !== rid) return false;
    // Micro-interaction: pop
    const el = dom.stages[id];
    if (el) { el.style.animation = 'stagePopIn 0.3s var(--spring)'; setTimeout(() => el.style.animation = '', 300); }
    setStage(id, statusClass(status));
    if (connIdx !== undefined) litConn(connIdx, status);
    addLog(STAGE_LABELS[id], text, status, true);
    completedStages = idx + 1;
    dom.stageCount.textContent = completedStages + ' / 8 stages';
    await sleep(60);
    return true;
  }

  async function failFrom(startIdx, rid, reason) {
    const remaining = STAGE_IDS.slice(startIdx);
    for (let i = 0; i < remaining.length; i++) {
      const gi = startIdx + i;
      const ci = CONN_BEFORE_STAGE[gi];
      if (ci !== undefined) litConn(ci, 'err');
      setStage(remaining[i], 'error');
      updateProgress(gi, 'error');
      const msg = i === remaining.length - 1 ? '\u201c' + reason + '\u201d' : 'skipped';
      addLog(STAGE_LABELS[remaining[i]], msg, 'err', true);
      await sleep(50);
    }
  }

  /* ── Progress bar on ID card ─── */
  function updateProgress(activeIdx, overrideStatus) {
    const steps = dom.idProgress.querySelectorAll('.prog-step');
    steps.forEach((s, i) => {
      s.className = 'prog-step';
      if (i < activeIdx) s.classList.add('done');
      else if (i === activeIdx) s.classList.add(overrideStatus || 'active');
    });
  }

  /* ── Conn & particle helpers ─── */
  function litConn(i, status) {
    const cls = 'lit-' + (status === 'ok' ? 'ok' : status === 'err' ? 'err' : status === 'pcc' ? 'pcc' : 'active');
    dom.conns[i].classList.add(cls); dom.arrows[i].classList.add(cls);
  }
  function animateParticle(i) {
    const p = dom.particles[i], line = dom.conns[i];
    const x1 = +line.getAttribute('x1'), y1 = +line.getAttribute('y1'), x2 = +line.getAttribute('x2'), y2 = +line.getAttribute('y2');
    p.setAttribute('cx', x1); p.setAttribute('cy', y1); p.classList.add('running');
    const dur = 200, start = performance.now();
    function tick(now) {
      const t = Math.min((now - start) / dur, 1);
      p.setAttribute('cx', x1 + (x2 - x1) * t); p.setAttribute('cy', y1 + (y2 - y1) * t);
      if (t < 1) requestAnimationFrame(tick); else p.classList.remove('running');
    }
    requestAnimationFrame(tick);
  }

  /* ── Classification ─── */
  function classify(text) {
    const t = text.toLowerCase();

    // Handle awaiting slot for multi-turn context
    if (dialogState.awaiting_slot === 'timer_duration') {
      const m = t.match(/(\d+)\s*(minute|min|second|sec|hour|hr)/);
      if (m) {
        const dur = `${m[1]} ${m[2]}s`;
        return { supported: true, intent: 'SET_TIMER', confidence: 0.98, routeType: 'local', servers: ['com.apple.timer.mcp'], privacyClass: 'local_safe', params: { duration: dur } };
      }
      const m2 = t.match(/^(\d+)$/);
      if (m2) {
        const dur = `${m2[1]} minutes`;
        return { supported: true, intent: 'SET_TIMER', confidence: 0.96, routeType: 'local', servers: ['com.apple.timer.mcp'], privacyClass: 'local_safe', params: { duration: dur } };
      }
    }

    // Memory / context
    if (/(do that again|repeat|again|redo)/.test(t))
      return { supported: true, intent: 'REPEAT_LAST', confidence: 0.95, routeType: 'local', servers: ['com.apple.clipboard.mcp'], privacyClass: 'local_safe' };
    if (/(what did i|last command|history|what was)/.test(t))
      return { supported: true, intent: 'RECALL_HISTORY', confidence: 0.93, routeType: 'local', servers: ['com.apple.clipboard.mcp'], privacyClass: 'local_safe' };
    // Timer
    if (/timer|countdown|alarm/.test(t)) {
      const m = t.match(/(\d+)\s*(minute|min|second|sec|hour|hr)/);
      if (m) {
        const dur = `${m[1]} ${m[2]}s`;
        return { supported: true, intent: 'SET_TIMER', confidence: 0.96, routeType: 'local', servers: ['com.apple.timer.mcp'], privacyClass: 'local_safe', params: { duration: dur } };
      } else {
        return { supported: true, intent: 'MISSING_SLOT', confidence: 0.90, routeType: 'local', servers: [], privacyClass: 'local_safe', params: { slot: "timer_duration", message: "For how long?" } };
      }
    }
    // Music
    if (/youtube|music|jazz|song|play|spotify/.test(t))
      return { supported: true, intent: 'PLAY_MUSIC', confidence: 0.93, routeType: 'remote', servers: ['com.google.youtubemusic'], privacyClass: 'remote_media' };
    // Weather
    if (/weather|temperature|forecast|rain|sunny/.test(t))
      return { supported: true, intent: 'GET_WEATHER', confidence: 0.94, routeType: 'remote', servers: ['com.apple.weather.mcp'], privacyClass: 'remote_data' };
    // Screenshot
    if (/screenshot|screen\s*cap|capture\s*(the\s*)?screen|snap/.test(t))
      return { supported: true, intent: 'TAKE_SCREENSHOT', confidence: 0.95, routeType: 'local', servers: ['com.apple.screenshot.mcp'], privacyClass: 'local_safe' };
    // Clipboard
    if (/clipboard|paste|what.*copied|copy that/.test(t))
      return { supported: true, intent: 'CLIPBOARD', confidence: 0.92, routeType: 'local', servers: ['com.apple.clipboard.mcp'], privacyClass: 'local_safe' };
    // System info
    if (/battery|cpu|memory|ram|disk|system\s*info|storage/.test(t))
      return { supported: true, intent: 'SYSTEM_INFO', confidence: 0.94, routeType: 'local', servers: ['com.apple.systeminfo.mcp'], privacyClass: 'local_safe' };
    // Volume
    if (/volume|mute|unmute|louder|quieter|sound/.test(t))
      return { supported: true, intent: 'VOLUME_CONTROL', confidence: 0.93, routeType: 'local', servers: ['com.apple.volume.mcp'], privacyClass: 'local_safe' };
    // Notes
    if (/(create|make|write|add)\s*(a\s*)?note/.test(t))
      return { supported: true, intent: 'CREATE_NOTE', confidence: 0.91, routeType: 'local', servers: ['com.apple.notes.mcp'], privacyClass: 'local_safe' };
    // Reminders
    if (/remind|reminder/.test(t))
      return { supported: true, intent: 'CREATE_REMINDER', confidence: 0.92, routeType: 'local', servers: ['com.apple.reminders.mcp'], privacyClass: 'local_safe' };
    // Finder
    if (/(open|show)\s*(the\s*)?(downloads?|documents?|desktop|home|finder|folder)/.test(t))
      return { supported: true, intent: 'OPEN_FINDER', confidence: 0.93, routeType: 'local', servers: ['com.apple.finder.mcp'], privacyClass: 'local_safe' };
    // Cross-context: Messages + Calendar
    if (/message/.test(t) && /(follow-up|follow up|meeting|calendar)/.test(t))
      return { supported: true, intent: 'FOLLOWUP_FROM_MESSAGE', confidence: 0.91, routeType: 'pcc', servers: ['com.apple.messages.mcp', 'com.apple.calendar.mcp'], privacyClass: 'cross_context_local' };
    // Web search
    if (/search|google|look up/.test(t))
      return { supported: true, intent: 'WEB_SEARCH', confidence: 0.90, routeType: 'remote', servers: ['com.apple.websearch.mcp'], privacyClass: 'external_search' };
    // Maps
    if (/map|direction|navigate|where is/.test(t))
      return { supported: true, intent: 'OPEN_MAPS', confidence: 0.92, routeType: 'remote', servers: ['com.apple.maps.mcp'], privacyClass: 'remote_data' };
    // Send message
    if (/send.*(message|text|imessage)/.test(t))
      return { supported: true, intent: 'SEND_MESSAGE', confidence: 0.89, routeType: 'local', servers: ['com.apple.messages.mcp'], privacyClass: 'local_safe' };
    // Calendar event
    if (/(create|add|schedule|new).*(event|meeting|appointment)/.test(t))
      return { supported: true, intent: 'CREATE_EVENT', confidence: 0.90, routeType: 'local', servers: ['com.apple.calendar.mcp'], privacyClass: 'local_safe' };
    // Generic open app
    if (/open\s+(\w+)/.test(t)) {
      return { supported: true, intent: 'OPEN_APP', confidence: 0.88, routeType: 'local', servers: ['com.apple.finder.mcp'], privacyClass: 'local_safe' };
    }

    // Date & Time
    if (/time|date|day is it/.test(t) && !/calculate|math|times/.test(t)) // Avoid conflict with calculator
      return { supported: true, intent: 'GET_DATE_TIME', confidence: 0.96, routeType: 'local', servers: ['com.apple.clock.mcp'], privacyClass: 'local_safe' };
    // Calculator
    if (/calculate|math|plus|minus|times|divided/.test(t))
      return { supported: true, intent: 'CALCULATE', confidence: 0.95, routeType: 'local', servers: ['com.apple.calculator.mcp'], privacyClass: 'local_safe', params: { expression: t } };
    // Joke
    if (/joke|laugh/.test(t))
      return { supported: true, intent: 'TELL_JOKE', confidence: 0.92, routeType: 'local', servers: ['com.entertainment.jokes.mcp'], privacyClass: 'local_safe' };
    // Quote
    if (/quote|inspire|wisdom|motivation/.test(t))
      return { supported: true, intent: 'GET_QUOTE', confidence: 0.91, routeType: 'local', servers: ['com.entertainment.quotes.mcp'], privacyClass: 'local_safe' };
    // Coin Flip
    if (/flip.*coin|heads.*tails/.test(t))
      return { supported: true, intent: 'FLIP_COIN', confidence: 0.94, routeType: 'local', servers: ['com.tools.random.mcp'], privacyClass: 'local_safe' };
    // Dice Roll
    if (/roll.*(die|dice)/.test(t))
      return { supported: true, intent: 'ROLL_DIE', confidence: 0.94, routeType: 'local', servers: ['com.tools.random.mcp'], privacyClass: 'local_safe' };
    // Dictionary
    if (/define|meaning of|definition/.test(t)) {
       const word = t.replace(/(define|meaning of|definition of|what is the)\s*/, '').trim();
       return { supported: true, intent: 'DEFINE_WORD', confidence: 0.92, routeType: 'remote', servers: ['com.reference.dictionary.mcp'], privacyClass: 'external_search', params: { word } };
    }
    // Currency
    if (/convert.*(currency|usd|eur|gbp|yen)|price of/.test(t))
      return { supported: true, intent: 'CONVERT_CURRENCY', confidence: 0.90, routeType: 'remote', servers: ['com.finance.currency.mcp'], privacyClass: 'external_search', params: { query: t } };
    // Local IP
    if (/my ip|ip address/.test(t))
      return { supported: true, intent: 'GET_IP', confidence: 0.95, routeType: 'local', servers: ['com.network.ip.mcp'], privacyClass: 'local_safe' };
    // Uptime
    if (/uptime|how long.*running/.test(t))
      return { supported: true, intent: 'GET_UPTIME', confidence: 0.93, routeType: 'local', servers: ['com.system.uptime.mcp'], privacyClass: 'local_safe' };

    return { supported: false, intent: 'UNSUPPORTED', confidence: 0.58, routeType: 'none', servers: [], privacyClass: 'unknown' };
  }
  function privacyCheck(plan, env) {
    if (plan.privacyClass === 'external_search' && env.privacyMode === 'ON') return { approved: false, label: 'BLOCKED · privacy mode ON' };
    if (plan.routeType === 'local') return { approved: true, label: 'LOCAL · approved' };
    if (plan.routeType === 'pcc') return { approved: true, label: 'PCC · approved' };
    if (plan.routeType === 'remote') return { approved: true, label: 'REMOTE · approved' };
    return { approved: false, label: 'BLOCKED · unsupported' };
  }
  function routeCheck(plan, env) {
    if (plan.routeType === 'none') return { ok: false, routeType: 'none', label: 'no route', servers: [] };
    if (plan.routeType === 'remote' && env.networkMode === 'OFFLINE') return { ok: false, routeType: 'remote', label: 'REMOTE · network unavailable', servers: plan.servers };
    return { ok: true, routeType: plan.routeType, label: plan.routeType.toUpperCase() + ' route', servers: plan.servers };
  }
  function execute(plan) {
    switch (plan.intent) {
      case 'MISSING_SLOT': return { log: 'dialogue · clarifying', entityId: 'dlg_' + uid(), response: plan.params ? plan.params.message : 'Can you clarify?' };
      case 'SET_TIMER': return { log: 'timer · armed for duration', entityId: 'timer_' + uid(), response: 'Timer set' };
      case 'PLAY_MUSIC': return { log: 'youtube_music · playback started', entityId: 'music_' + uid(), response: 'Playing on YouTube Music' };
      case 'GET_WEATHER': return { log: 'weather · fetched', entityId: 'weather_' + uid(), response: 'Weather data retrieved' };
      case 'TAKE_SCREENSHOT': return { log: 'screenshot · saved', entityId: 'ss_' + uid(), response: 'Screenshot saved to Desktop' };
      case 'CLIPBOARD': return { log: 'clipboard · read', entityId: 'clip_' + uid(), response: 'Clipboard contents retrieved' };
      case 'SYSTEM_INFO': return { log: 'sysinfo · fetched', entityId: 'sys_' + uid(), response: 'System info retrieved' };
      case 'VOLUME_CONTROL': return { log: 'volume · adjusted', entityId: 'vol_' + uid(), response: 'Volume adjusted' };
      case 'CREATE_NOTE': return { log: 'notes · created', entityId: 'note_' + uid(), response: 'Note created in Apple Notes' };
      case 'CREATE_REMINDER': return { log: 'reminders · added', entityId: 'rem_' + uid(), response: 'Reminder added to Reminders' };
      case 'OPEN_FINDER': return { log: 'finder · opened', entityId: 'finder_' + uid(), response: 'Opened folder in Finder' };
      case 'FOLLOWUP_FROM_MESSAGE': return { log: 'messages + calendar · opened', entityId: 'followup_' + uid(), response: 'Opened Messages and Calendar' };
      case 'WEB_SEARCH': return { log: 'web_search · completed', entityId: 'search_' + uid(), response: 'Search results opened' };
      case 'OPEN_MAPS': return { log: 'maps · opened', entityId: 'maps_' + uid(), response: 'Opening Apple Maps' };
      case 'SEND_MESSAGE': return { log: 'messages · opened', entityId: 'msg_' + uid(), response: 'Opening Messages' };
      case 'CREATE_EVENT': return { log: 'calendar · opened', entityId: 'event_' + uid(), response: 'Opening Calendar' };
      case 'OPEN_APP': return { log: 'app · launched', entityId: 'app_' + uid(), response: 'Opening app' };
      case 'REPEAT_LAST': return { log: 'replay · last command', entityId: 'replay_' + uid(), response: 'Repeating last command' };
      case 'RECALL_HISTORY': return { log: 'history · recalled', entityId: 'hist_' + uid(), response: 'Showing recent history' };
      case 'GET_DATE_TIME': return { log: 'clock · fetched', entityId: 'time_' + uid(), response: 'It is ' + new Date().toLocaleString() };
      case 'CALCULATE': return { log: 'calc · computed', entityId: 'calc_' + uid(), response: 'The answer is 42 (simulated)' };
      case 'TELL_JOKE': return { log: 'joke · told', entityId: 'joke_' + uid(), response: 'Why did the chicken cross the road? To get to the other side.' };
      case 'GET_QUOTE': return { log: 'quote · fetched', entityId: 'quote_' + uid(), response: 'The only way to do great work is to love what you do.' };
      case 'FLIP_COIN': return { log: 'coin · flipped', entityId: 'coin_' + uid(), response: Math.random() > 0.5 ? 'Heads' : 'Tails' };
      case 'ROLL_DIE': return { log: 'die · rolled', entityId: 'die_' + uid(), response: '' + Math.floor(Math.random() * 6 + 1) };
      case 'DEFINE_WORD': return { log: 'dictionary · defined', entityId: 'def_' + uid(), response: 'Definition of ' + (plan.params.word || 'word') + ': A word used in this demo.' };
      case 'CONVERT_CURRENCY': return { log: 'currency · converted', entityId: 'curr_' + uid(), response: '1 USD is approximately 0.94 EUR' };
      case 'GET_IP': return { log: 'ip · fetched', entityId: 'ip_' + uid(), response: 'Your IP address is 127.0.0.1 (simulated)' };
      case 'GET_UPTIME': return { log: 'uptime · fetched', entityId: 'uptime_' + uid(), response: 'System status: up 1 day, 2:30' };
      default: return { log: 'no-op', entityId: session.lastEntity, response: 'I could not complete that command' };
    }
  }

  /* ── UI helpers ─── */
  function setStage(id, cls) {
    const el = dom.stages[id]; if (!el) return;
    el.classList.remove('idle', 'active', 'success', 'error', 'pcc'); el.classList.add(cls);
  }
  function statusClass(s) { return s === 'ok' ? 'success' : s === 'err' ? 'error' : s === 'pcc' ? 'pcc' : 'idle'; }
  function resetAll() {
    STAGE_IDS.forEach(id => setStage(id, 'idle'));
    // Bug 1 fix: use setAttribute for reliable SVG class handling
    for (let i = 0; i <= 6; i++) { dom.conns[i].setAttribute('class', 'conn-line'); dom.arrows[i].setAttribute('class', 'conn-arrow'); dom.particles[i].classList.remove('running'); }
    dom.idProgress.querySelectorAll('.prog-step').forEach(s => s.className = 'prog-step');
    dom.stageCount.textContent = '0 / 8 stages';
  }
  let logDelay = 0;
  function addLog(tag, text, status, mark) {
    // Remove empty state
    const empty = dom.logs.querySelector('.empty-state'); if (empty) empty.remove();
    const line = document.createElement('div');
    line.className = 'log-line';
    line.style.animationDelay = logDelay + 'ms';
    logDelay += 40;
    let m = '';
    if (mark) {
      if (status === 'ok') m = '<span class="mark-ok">✓</span>';
      else if (status === 'err') m = '<span class="mark-err">✗</span>';
      else if (status === 'pcc') m = '<span class="mark-pcc">△</span>';
    }
    const pad = ('[' + tag + ']').padEnd(14);
    line.innerHTML = '<span class="stage-tag">' + pad + '</span>  ' + esc(text) + (m ? '  ' + m : '');
    dom.logs.appendChild(line);
    dom.logs.scrollTop = dom.logs.scrollHeight;
  }
  function clearLogs() { dom.logs.innerHTML = ''; logDelay = 0; }

  function renderServers() {
    const online = getNetwork() === 'ONLINE';
    dom.serverList.innerHTML = '';
    SERVERS.forEach(s => {
      const on = s.needsNetwork ? online : true;
      const row = document.createElement('div');
      row.className = 'server-row'; row.dataset.sid = s.id;
      row.innerHTML = '<span class="srv-name">' + s.id + '</span><span class="srv-scope">' + s.scope + '</span><span class="srv-status"><span class="srv-dot ' + (on ? 'on' : 'off') + '"></span>' + (on ? 'online' : 'offline') + '</span>';
      dom.serverList.appendChild(row);
    });
  }

  function renderSession() {
    dom.sId.textContent = session.id;
    dom.sActive.textContent = session.active ? 'yes' : 'no';
    dom.sTurns.textContent = session.turns;
    dom.sEntity.textContent = session.lastEntity;
    const exp = dom.sExpiry;
    exp.textContent = session.expiresIn + 's';
    exp.className = 's-val';
    if (session.expiresIn <= 10) exp.classList.add('expiry-crit');
    else if (session.expiresIn <= 30) exp.classList.add('expiry-warn');
  }

  function setDisabled(v) {
    dom.speak.disabled = v; dom.input.disabled = v; dom.micBtn.disabled = v;
    dom.presets.querySelectorAll('button').forEach(b => b.disabled = v);
  }
  function done() {
    const latMs = performance.now() - pipelineStartTime;
    if (currentRunMeta && currentRunMeta.cmd) {
      recordRun(currentRunMeta.cmd, currentRunMeta.intent, currentRunMeta.confidence, currentRunMeta.routeType, latMs, currentRunMeta.succeeded);
    }
    currentRunMeta = null;
    running = false; setDisabled(false);
    // UX: Reset loading state
    dom.speak.innerHTML = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg> Run';
    dom.speak.classList.remove('processing');

    // Bug 2 fix: respect session.active state for live dot
    if (session.active) dom.liveDot.classList.remove('off');
    else dom.liveDot.classList.add('off');
  }

  /* ── Analytics Engine ─── */
  const analytics = { runs: [], intents: {} };
  const INTENT_COLORS = {
    SET_TIMER: 'var(--green)', PLAY_MUSIC: 'var(--red)', FOLLOWUP_FROM_MESSAGE: 'var(--yellow)',
    WEB_SEARCH: 'var(--purple)', GET_WEATHER: 'var(--blue)', TAKE_SCREENSHOT: 'var(--green)',
    CLIPBOARD: 'var(--blue)', SYSTEM_INFO: 'var(--yellow)', VOLUME_CONTROL: 'var(--purple)',
    CREATE_NOTE: 'var(--green)', CREATE_REMINDER: 'var(--blue)', OPEN_FINDER: 'var(--yellow)',
    OPEN_MAPS: 'var(--red)', SEND_MESSAGE: 'var(--purple)', CREATE_EVENT: 'var(--blue)',
    OPEN_APP: 'var(--green)', REPEAT_LAST: 'var(--yellow)', RECALL_HISTORY: 'var(--blue)',
    GET_DATE_TIME: 'var(--green)', CALCULATE: 'var(--blue)', TELL_JOKE: 'var(--purple)',
    GET_QUOTE: 'var(--yellow)', FLIP_COIN: 'var(--green)', ROLL_DIE: 'var(--green)',
    DEFINE_WORD: 'var(--blue)', CONVERT_CURRENCY: 'var(--yellow)', GET_IP: 'var(--purple)',
    GET_UPTIME: 'var(--green)', UNSUPPORTED: 'var(--red)'
  };

  function recordRun(cmd, intent, confidence, routeType, latencyMs, succeeded) {
    const entry = { id: analytics.runs.length + 1, cmd, intent, confidence, routeType, latencyMs, succeeded, ts: Date.now() };
    analytics.runs.push(entry);
    analytics.intents[intent] = (analytics.intents[intent] || 0) + 1;
    refreshAnalytics();
  }

  function percentile(arr, p) {
    if (!arr.length) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const idx = Math.ceil(p / 100 * sorted.length) - 1;
    return sorted[Math.max(0, idx)];
  }

  function refreshAnalytics() {
    const runs = analytics.runs;
    if (!runs.length) return;

    // Totals
    const total = runs.length;
    const successes = runs.filter(r => r.succeeded).length;
    const rate = total > 0 ? (successes / total * 100) : 0;
    const confs = runs.map(r => r.confidence);
    const lats = runs.map(r => r.latencyMs);
    const avgConf = confs.reduce((a, b) => a + b, 0) / confs.length;
    const avgLat = lats.reduce((a, b) => a + b, 0) / lats.length;
    const minConf = Math.min(...confs);
    const maxConf = Math.max(...confs);
    const minLat = Math.min(...lats);
    const maxLat = Math.max(...lats);

    // Metrics
    document.getElementById('m-total').textContent = total;
    document.getElementById('m-rate').textContent = (total / Math.max(1, (Date.now() - runs[0].ts) / 60000)).toFixed(1) + ' / min';
    document.getElementById('m-success').textContent = rate.toFixed(0) + '%';
    document.getElementById('m-success-n').textContent = successes + ' of ' + total + ' succeeded';
    document.getElementById('m-conf').textContent = (avgConf * 100).toFixed(0) + '%';
    document.getElementById('m-conf-range').textContent = (minConf * 100).toFixed(0) + '–' + (maxConf * 100).toFixed(0) + '%';
    document.getElementById('m-latency').textContent = avgLat.toFixed(0) + 'ms';
    document.getElementById('m-latency-range').textContent = minLat.toFixed(0) + '–' + maxLat.toFixed(0) + 'ms';

    // Percentiles
    const p50 = percentile(lats, 50), p90 = percentile(lats, 90), p99 = percentile(lats, 99);
    document.getElementById('p50').textContent = p50.toFixed(0) + 'ms';
    document.getElementById('p90').textContent = p90.toFixed(0) + 'ms';
    document.getElementById('p99').textContent = p99.toFixed(0) + 'ms';
    const maxP = Math.max(p99, 1);
    document.getElementById('p50bar').style.width = (p50 / maxP * 100) + '%';
    document.getElementById('p90bar').style.width = (p90 / maxP * 100) + '%';
    document.getElementById('p99bar').style.width = '100%';

    // Pulse the metrics grid to show update
    const mGrid = document.getElementById('metricsGrid');
    if (runs.length > 1) {
      mGrid.style.animation = 'none';
      void mGrid.offsetWidth; // trigger reflow
      mGrid.style.animation = 'stagePopIn 0.3s var(--spring)';
    }

    // Sparkline
    drawSparkline(lats.slice(-30));

    // Intent breakdown
    const bd = document.getElementById('intentBreakdown');
    const sorted = Object.entries(analytics.intents).sort((a, b) => b[1] - a[1]);
    const maxCount = sorted[0] ? sorted[0][1] : 1;
    bd.innerHTML = sorted.map(([intent, count]) => {
      const pct = (count / maxCount * 100).toFixed(0);
      const color = INTENT_COLORS[intent] || 'var(--blue)';
      return '<div class="intent-row">' +
        '<span class="intent-name">' + intent + '</span>' +
        '<div class="intent-bar-bg"><div class="intent-bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div>' +
        '<span class="intent-count">' + count + '</span></div>';
    }).join('');

    // History table
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = runs.slice().reverse().map((r, i) => {
      const dotCls = r.succeeded ? 's-ok' : 's-err';
      const statusTxt = r.succeeded ? 'OK' : 'FAIL';
      const cmdShort = r.cmd.length > 28 ? r.cmd.slice(0, 28) + '…' : r.cmd;
      const delay = Math.min(i * 0.04, 0.4).toFixed(2);
      return '<tr style="animation: fadeUp 0.35s var(--ease-out) ' + delay + 's both">' +
        '<td>' + r.id + '</td>' +
        '<td>' + esc(cmdShort) + '</td>' +
        '<td>' + r.intent + '</td>' +
        '<td>' + (r.confidence * 100).toFixed(0) + '%</td>' +
        '<td>' + r.routeType.toUpperCase() + '</td>' +
        '<td>' + r.latencyMs.toFixed(0) + 'ms</td>' +
        '<td><span class="status-dot ' + dotCls + '"></span>' + statusTxt + '</td></tr>';
    }).join('');
  }

  function drawSparkline(data) {
    const c = document.getElementById('sparkCanvas');
    const ctx = c.getContext('2d');
    c.width = c.offsetWidth * 2; c.height = 128;
    ctx.clearRect(0, 0, c.width, c.height);
    if (data.length < 2) return;
    const max = Math.max(...data, 1);
    const pad = 8;
    const w = c.width - pad * 2, h = c.height - pad * 2;
    // Gradient fill
    const grad = ctx.createLinearGradient(0, pad, 0, c.height);
    grad.addColorStop(0, 'rgba(108,142,239,0.2)');
    grad.addColorStop(1, 'rgba(108,142,239,0)');
    ctx.beginPath();
    ctx.moveTo(pad, pad + h);
    data.forEach((v, i) => {
      const x = pad + (i / (data.length - 1)) * w;
      const y = pad + h - (v / max) * h;
      ctx.lineTo(x, y);
    });
    ctx.lineTo(pad + w, pad + h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();
    // Line
    ctx.beginPath();
    data.forEach((v, i) => {
      const x = pad + (i / (data.length - 1)) * w;
      const y = pad + h - (v / max) * h;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.strokeStyle = 'rgba(108,142,239,0.7)';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.stroke();
    // Dots
    data.forEach((v, i) => {
      const x = pad + (i / (data.length - 1)) * w;
      const y = pad + h - (v / max) * h;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(108,142,239,0.9)';
      ctx.fill();
    });
  }



  /* ── Utilities ─── */
  // Bug 4 fix: preserve original casing (classify already lowercases internally)
  function normalise(s) { return s.trim().replace(/\s+/g, ' '); }
  function wakeScore(c) { return Math.min(0.98, 0.91 + (c.length % 5) * 0.01); }
  function randInt(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
  function uid() { const a = 'abcdefghijklmnopqrstuvwxyz0123456789'; let o = ''; for (let i = 0; i < 6; i++) o += a[Math.floor(Math.random() * a.length)]; return o; }
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
  // Bug 7 fix: also escape single quotes for defense-in-depth XSS protection
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;'); }
})();
