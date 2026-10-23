/**
 * SPOTLIGHT — Phone Remote Client Script
 * Powers the tactile Curiosity Remote mobile web interface.
 */

(function () {
  const askBtn = document.getElementById("askBtn");
  const questionInput = document.getElementById("questionInput");
  const nowWatchingInput = document.getElementById("nowWatchingInput");
  const targetTitle = document.getElementById("targetTitle");
  const targetStatus = document.getElementById("targetStatus");
  const targetChannel = document.getElementById("targetChannel");
  const targetTimecode = document.getElementById("targetTimecode");
  const companionInsight = document.getElementById("companionInsight");
  const historyList = document.getElementById("historyList");
  const dismissBtn = document.getElementById("dismissBtn");
  const resetBtn = document.getElementById("resetBtn");
  const syncStatus = document.getElementById("syncStatus");
  const beatTabs = document.querySelectorAll(".beat-tab-btn");
  const snapBtn = document.getElementById("snapBtn");
  const snapInput = document.getElementById("snapInput");
  const snapPreviewRow = document.getElementById("snapPreviewRow");
  const snapThumbnail = document.getElementById("snapThumbnail");
  const snapFilename = document.getElementById("snapFilename");
  const snapLabel = document.getElementById("snapLabel");
  const snapClearBtn = document.getElementById("snapClearBtn");

  // Custom video URL push to TV
  const pushUrlBtn = document.getElementById("pushUrlBtn");
  const pushUrlInput = document.getElementById("pushUrlInput");
  const pushTitleInput = document.getElementById("pushTitleInput");

  let currentBeat = "kids";
  let scenesData = {};
  let ws = null;
  let isAsking = false;
  let currentFrameB64 = null;

  // --- Session-Isolated WebSocket Hub (/ws/session/{session_id}) ---
  let sessionWs = null;
  let speechRec = null;
  const _sessionParam = new URLSearchParams(window.location.search).get("session");
  let sessionId = _sessionParam || localStorage.getItem("spotlight_pairing_code") || "";

  function connectSessionWS() {
    if (!sessionId) { _showPairingPrompt(); _renderTvState("unpaired"); return; }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const hubUrl = `${protocol}//${window.location.host}/ws/session/${sessionId}`;
    sessionWs = new WebSocket(hubUrl);

    sessionWs.onopen = () => {
      console.log(`[Remote] Connected to session hub: ${sessionId}`);
      _hidePairingPrompt();
      _renderTvState("idle");
    };

    sessionWs.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg && msg.kind === "tv_voice_state") _renderTvState(msg.state);
      } catch (_) {}
    };

    sessionWs.onclose = () => {
      _renderTvState("reconnecting");
      setTimeout(connectSessionWS, 1500);
    };

    sessionWs.onerror = () => {
      sessionWs.close();
    };
  }

  // --- Pairing + TV voice-state mirror ---
  function _showPairingPrompt() {
    const p = document.getElementById("pairingPrompt");
    if (p) p.style.display = "block";
  }
  function _hidePairingPrompt() {
    const p = document.getElementById("pairingPrompt");
    if (p) p.style.display = "none";
  }
  function _renderTvState(state) {
    const el = document.getElementById("tvVoiceState");
    if (!el) return;
    const labels = { idle: "TV IDLE", listening: "TV LISTENING", thinking: "TV THINKING",
      speaking: "TV SPEAKING", reconnecting: "RECONNECTING", unpaired: "NOT PAIRED" };
    el.textContent = labels[state] || ("TV " + String(state).toUpperCase());
    el.dataset.state = state;
  }
  function pairWithCode(code) {
    code = (code || "").trim().toUpperCase();
    if (!code) return;
    localStorage.setItem("spotlight_pairing_code", code);
    sessionId = code;
    try { if (sessionWs) sessionWs.close(); } catch (_) {}
    _hidePairingPrompt();
    connectSessionWS();
  }

  // Pairing form wiring
  (function _wirePairing() {
    const bind = () => {
      const btn = document.getElementById("pairBtn");
      const input = document.getElementById("pairInput");
      if (!btn || !input) return;
      btn.addEventListener("click", () => pairWithCode(input.value));
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") pairWithCode(input.value); });
      if (sessionId) input.value = sessionId;
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind);
    else bind();
  })();

  function publishHub(msg) {
    if (sessionWs && sessionWs.readyState === WebSocket.OPEN) {
      sessionWs.send(JSON.stringify(msg));
    }
  }

  // Push custom video URL + title to TV via session hub
  if (pushUrlBtn) {
    pushUrlBtn.addEventListener("click", () => {
      const url = (pushUrlInput.value || "").trim();
      const title = (pushTitleInput.value || "").trim() || "Custom Video";
      if (!url) return;
      publishHub({ kind: "play_url", url: url, title: title });
      // Also update the "now watching" field so ASK uses this title as context
      if (nowWatchingInput) nowWatchingInput.value = title;
      if (targetTitle) targetTitle.textContent = title;
    });
  }

  connectSessionWS();

  // Beat default questions map
  const defaultQuestions = {
    kids: "Why is the sky blue?",
    movie: "who is that man?",
    sports: "Why was that a foul?",
    news: "Is that claim true?",
    cooking: "What spice did they just add?",
    esports: "Why did they lose that fight?",
    shopping: "What shoes is he wearing?",
    language: "What did they just say?",
  };

  // Setup WebSocket connection
  function connectWS() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      if (syncStatus) syncStatus.textContent = "TV CONNECTED";
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.state) {
          syncWithState(data.state, data.scene);
        }
        if (data.history) {
          renderHistory(data.history);
        }
      } catch (err) {
        console.error("[Remote] WS Parse Error", err);
      }
    };

    ws.onclose = () => {
      if (syncStatus) syncStatus.textContent = "RECONNECTING...";
      setTimeout(connectWS, 1500);
    };

    ws.onerror = () => {
      ws.close();
    };
  }

  function syncWithState(state, scene) {
    currentBeat = state.current_beat;

    // Update active beat tab
    beatTabs.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.beat === currentBeat);
    });

    if (scene) {
      if (targetTitle) targetTitle.textContent = scene.title;
      if (targetChannel) targetChannel.textContent = scene.channel;
      if (targetTimecode) targetTimecode.textContent = scene.timestamp;
    }

    // Status indicator
    if (targetStatus) {
      if (state.status === "analyzing") {
        targetStatus.textContent = "ANALYZING ON TV...";
        setAskButtonState(true);
      } else if (state.status === "answered") {
        targetStatus.textContent = "ANSWER ACTIVE ON TV";
        setAskButtonState(false);
      } else {
        targetStatus.textContent = "PLAYING";
        setAskButtonState(false);
      }
    }

    // Prefill question if input is empty or matches previous beat's default
    if (questionInput) {
      const currentVal = questionInput.value.trim();
      const isDefault = Object.values(defaultQuestions).includes(currentVal) || currentVal === "";
      if (isDefault) {
        questionInput.value = defaultQuestions[currentBeat] || "";
      }
    }
  }

  function setAskButtonState(isBusy) {
    if (!askBtn) return;
    isAsking = isBusy;
    if (isBusy) {
      askBtn.classList.add("analyzing");
      askBtn.querySelector(".btn-primary-text").textContent = "ANALYZING...";
      askBtn.querySelector(".btn-sub-text").textContent = "TV FRAME FROZEN";
    } else {
      askBtn.classList.remove("analyzing");
      askBtn.querySelector(".btn-primary-text").textContent = "ASK";
      askBtn.querySelector(".btn-sub-text").textContent = "TAP TO FREEZE TV & EXPLAIN";
    }
  }

  // Handle Big Ask Button Tap
  async function triggerAsk() {
    if (isAsking) return;

    const question = questionInput.value.trim() || defaultQuestions[currentBeat];
    const contextTitle = nowWatchingInput ? nowWatchingInput.value.trim() : "";
    setAskButtonState(true);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          beat_id: currentBeat,
          question: question,
          context_title: contextTitle || null,
          frame_b64: currentFrameB64 || null,
          source: "remote",
        }),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.session_item && data.session_item.companion_note) {
          if (companionInsight) {
            companionInsight.textContent = data.session_item.companion_note;
          }
        }
        await loadHistory();
      }
    } catch (err) {
      console.error("[Remote] Ask Error", err);
    } finally {
      setTimeout(() => setAskButtonState(false), 600);
    }
  }

  // Switch Beat Tabs
  beatTabs.forEach((tab) => {
    tab.addEventListener("click", async () => {
      const beat = tab.dataset.beat;
      currentBeat = beat;

      beatTabs.forEach((t) => t.classList.toggle("active", t === tab));
      if (questionInput) {
        questionInput.value = defaultQuestions[beat] || "";
      }

      try {
        await fetch("/api/beat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ beat_id: beat }),
        });
      } catch (err) {
        console.error("[Remote] Set beat error", err);
      }
    });
  });

  // Action Buttons
  if (askBtn) {
    askBtn.addEventListener("click", triggerAsk);
  }

  if (dismissBtn) {
    dismissBtn.addEventListener("click", async () => {
      try {
        await fetch("/api/dismiss", { method: "POST" });
      } catch (err) {
        console.error("[Remote] Dismiss error", err);
      }
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      try {
        if (nowWatchingInput) nowWatchingInput.value = "";
        clearSnap();
        await fetch("/api/reset", { method: "POST" });
        await loadHistory();
      } catch (err) {
        console.error("[Remote] Reset error", err);
      }
    });
  }

  // Camera / File input handling for "Snap the screen"
  function clearSnap() {
    currentFrameB64 = null;
    if (snapInput) snapInput.value = "";
    if (snapPreviewRow) snapPreviewRow.style.display = "none";
    if (snapThumbnail) snapThumbnail.src = "";
    if (snapLabel) snapLabel.textContent = "Snap the screen";
  }

  if (snapBtn && snapInput) {
    snapBtn.addEventListener("click", () => {
      snapInput.click();
    });

    snapInput.addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event) => {
        currentFrameB64 = event.target.result;
        if (snapThumbnail) snapThumbnail.src = currentFrameB64;
        if (snapFilename) snapFilename.textContent = file.name || "Screen photo attached";
        if (snapPreviewRow) snapPreviewRow.style.display = "flex";
        if (snapLabel) snapLabel.textContent = "Change screen snap";

        if (questionInput) {
          const val = questionInput.value.trim();
          if (Object.values(defaultQuestions).includes(val) || val === "") {
            questionInput.value = "What is on the screen right now?";
          }
        }
      };
      reader.readAsDataURL(file);
    });
  }

  if (snapClearBtn) {
    snapClearBtn.addEventListener("click", clearSnap);
  }

  // Load and render history
  async function loadHistory() {
    try {
      const res = await fetch("/api/history");
      if (res.ok) {
        const data = await res.json();
        renderHistory(data.history);
      }
    } catch (_) {}
  }

  function renderHistory(items) {
    if (!historyList) return;
    historyList.innerHTML = "";

    if (!items || items.length === 0) {
      const empty = document.createElement("div");
      empty.className = "history-item-row";
      empty.textContent = "No curiosity queries logged yet.";
      historyList.appendChild(empty);
      return;
    }

    items.slice(0, 5).forEach((item) => {
      const row = document.createElement("div");
      row.className = "history-item-row";

      const qSpan = document.createElement("span");
      qSpan.className = "history-item-q";
      qSpan.textContent = item.question;

      const catSpan = document.createElement("span");
      catSpan.textContent = item.category;

      row.appendChild(qSpan);
      row.appendChild(catSpan);
      historyList.appendChild(row);
    });
  }

  // Initial Sync
  connectWS();
  loadHistory();

  // ---- Push-to-talk voice Q&A loop (MediaRecorder + faster-whisper + Piper) ----
  const micBtn = document.getElementById("micBtn");
  const micIcon = document.getElementById("micIcon");
  const micLabel = document.getElementById("micLabel");
  const langSelect = document.getElementById("langSelect");

  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;
  let activeAudioStream = null;
  let currentPhoneAudio = null;

  function resetMicUI() {
    if (micBtn) {
      micBtn.classList.remove("recording", "processing", "speaking");
      micBtn.disabled = false;
    }
    if (micIcon) micIcon.textContent = "🎙️";
    if (micLabel) micLabel.textContent = "PUSH TO TALK";
  }

  function stopPhoneAudio() {
    if (currentPhoneAudio) {
      try {
        currentPhoneAudio.pause();
        currentPhoneAudio.currentTime = 0;
      } catch (_) {}
      currentPhoneAudio = null;
    }
  }

  async function speakOnPhone(text) {
    if (!text || !text.trim()) {
      resetMicUI();
      return;
    }
    try {
      if (micBtn) {
        micBtn.classList.remove("processing");
        micBtn.classList.add("speaking");
      }
      if (micIcon) micIcon.textContent = "🔊";
      if (micLabel) micLabel.textContent = "SPEAKING ANSWER...";

      const res = await fetch("/api/voice/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });

      if (!res.ok) {
        console.warn("[Remote] /api/voice/speak returned status", res.status);
        resetMicUI();
        return;
      }

      const audioBlob = await res.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      stopPhoneAudio();
      currentPhoneAudio = new Audio(audioUrl);
      currentPhoneAudio.onended = () => {
        resetMicUI();
        URL.revokeObjectURL(audioUrl);
      };
      currentPhoneAudio.onerror = (e) => {
        console.warn("[Remote] Phone audio play error", e);
        resetMicUI();
        URL.revokeObjectURL(audioUrl);
      };
      await currentPhoneAudio.play();
    } catch (err) {
      console.error("[Remote] speakOnPhone error", err);
      resetMicUI();
    }
  }

  async function handleVoiceTranscribeAndAsk(audioBlob) {
    if (micBtn) {
      micBtn.classList.remove("recording");
      micBtn.classList.add("processing");
    }
    if (micIcon) micIcon.textContent = "⏳";
    if (micLabel) micLabel.textContent = "TRANSCRIBING...";

    publishHub({ kind: "voice_state", state: "thinking", transcript: "" });

    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const resultStr = reader.result;
        const b64 = resultStr.includes(",") ? resultStr.split(",")[1] : resultStr;
        const mime = audioBlob.type || "audio/webm; codecs=opus";

        const res = await fetch("/api/voice/transcribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ audio_b64: b64, mime: mime }),
        });

        if (!res.ok) {
          throw new Error("Transcribe failed: " + res.status);
        }

        const data = await res.json();
        const recognizedText = (data.text || "").trim();
        const intent = data.intent;

        if (!recognizedText) {
          publishHub({ kind: "voice_state", state: "idle" });
          if (micIcon) micIcon.textContent = "⚠️";
          if (micLabel) micLabel.textContent = "NO SPEECH DETECTED";
          setTimeout(resetMicUI, 1800);
          return;
        }

        // Put transcribed text into questionInput
        if (questionInput) questionInput.value = recognizedText;

        // Device commands hit router first!
        if (intent && intent.type === "command") {
          console.log("[Remote] Device command classified:", intent);
          publishHub({
            kind: "control",
            action: intent.action,
            seconds: intent.seconds,
          });
          publishHub({ kind: "voice_state", state: "idle" });

          if (micIcon) micIcon.textContent = "⚡";
          const secStr = intent.seconds ? ` (${intent.seconds}s)` : "";
          if (micLabel) micLabel.textContent = `COMMAND: ${intent.action.toUpperCase()}${secStr}`;
          setTimeout(resetMicUI, 1600);
          return;
        }

        // Question intent continues to /api/ask pipeline
        publishHub({ kind: "voice_state", state: "thinking", transcript: recognizedText });
        if (micLabel) micLabel.textContent = "ASKING SPOTLIGHT...";
        setAskButtonState(true);

        // Auto-submit to existing /api/ask
        const askPayload = {
          beat_id: currentBeat,
          question: recognizedText,
          context_title: (nowWatchingInput && nowWatchingInput.value.trim()) || null,
          frame_b64: currentFrameB64 || null,
          source: "remote",
          lang: window.__spotlightLang || "en",
        };

        const askRes = await fetch("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(askPayload),
        });

        if (askRes.ok) {
          const askData = await askRes.json();
          if (askData.session_item && askData.session_item.companion_note && companionInsight) {
            companionInsight.textContent = askData.session_item.companion_note;
          }
          await loadHistory();

          // Play synthesized audio on phone
          if (askData.answer) {
            const answerSpeechText = `${askData.answer.title || ""}. ${askData.answer.primary_explanation || ""}`.trim();
            publishHub({
              kind: "voice_state",
              state: "speaking",
              transcript: askData.answer.title || answerSpeechText.slice(0, 60),
            });
            await speakOnPhone(answerSpeechText);
            publishHub({ kind: "voice_state", state: "idle" });
          } else {
            publishHub({ kind: "voice_state", state: "idle" });
            resetMicUI();
          }
        } else {
          publishHub({ kind: "voice_state", state: "idle" });
          resetMicUI();
        }
      } catch (err) {
        console.error("[Remote] Voice loop error", err);
        publishHub({ kind: "voice_state", state: "idle" });
        if (micIcon) micIcon.textContent = "❌";
        if (micLabel) micLabel.textContent = "VOICE FAILED";
        setTimeout(resetMicUI, 2000);
      } finally {
        setTimeout(() => setAskButtonState(false), 600);
      }
    };
    reader.readAsDataURL(audioBlob);
  }

  async function startRecording() {
    stopPhoneAudio();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Microphone access is not supported or requires a secure context (HTTPS / localhost).");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      activeAudioStream = stream;

      let mimeType = "audio/webm;codecs=opus";
      if (typeof MediaRecorder !== "undefined") {
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          if (MediaRecorder.isTypeSupported("audio/webm")) {
            mimeType = "audio/webm";
          } else if (MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")) {
            mimeType = "audio/ogg;codecs=opus";
          } else if (MediaRecorder.isTypeSupported("audio/mp4")) {
            mimeType = "audio/mp4";
          } else {
            mimeType = "";
          }
        }
      }

      const options = mimeType ? { mimeType } : undefined;
      mediaRecorder = new MediaRecorder(stream, options);
      audioChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, {
          type: mediaRecorder.mimeType || mimeType || "audio/webm",
        });
        handleVoiceTranscribeAndAsk(audioBlob);
      };

      mediaRecorder.start(100);
      isRecording = true;

      publishHub({ kind: "voice_state", state: "listening", transcript: "" });

      // Live partial transcript streaming if Web Speech API available
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRec) {
        try {
          speechRec = new SpeechRec();
          speechRec.continuous = true;
          speechRec.interimResults = true;
          speechRec.lang = window.__spotlightLang || "en-US";
          speechRec.onresult = (ev) => {
            let partial = "";
            for (let i = ev.resultIndex; i < ev.results.length; ++i) {
              partial += ev.results[i][0].transcript;
            }
            partial = partial.trim();
            if (partial) {
              publishHub({ kind: "voice_state", state: "listening", transcript: partial });
            }
          };
          speechRec.onerror = () => {};
          speechRec.start();
        } catch (_) {}
      }

      if (micBtn) {
        micBtn.classList.remove("processing", "speaking");
        micBtn.classList.add("recording");
      }
      if (micIcon) micIcon.textContent = "⏹️";
      if (micLabel) micLabel.textContent = "LISTENING... TAP TO STOP";
    } catch (err) {
      console.error("[Remote] Microphone start error", err);
      alert("Could not access microphone: " + (err.message || err));
      resetMicUI();
    }
  }

  function stopRecording() {
    if (!isRecording || !mediaRecorder) return;
    isRecording = false;
    if (speechRec) {
      try { speechRec.stop(); } catch (_) {}
      speechRec = null;
    }
    try {
      if (mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
      }
    } catch (e) {
      console.warn("mediaRecorder stop error", e);
    }
    if (activeAudioStream) {
      activeAudioStream.getTracks().forEach((track) => track.stop());
      activeAudioStream = null;
    }
  }

  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (isRecording) {
        stopRecording();
      } else {
        startRecording();
      }
    });
  }

  // ---- Language selector -> included in ask payload ----
  window.__spotlightLang = "en";
  if (langSelect) {
    langSelect.addEventListener("change", () => {
      window.__spotlightLang = langSelect.value;
    });
  }
  // patch ask payload: wrap fetch if it exists
  const _origFetch = window.fetch;
  window.fetch = function (url, opts) {
    try {
      if (typeof url === "string" && url.includes("/api/ask") && opts && opts.body) {
        const body = JSON.parse(opts.body);
        if (!body.lang) body.lang = window.__spotlightLang || "en";
        if (body.context_title === undefined && nowWatchingInput && nowWatchingInput.value.trim()) {
          body.context_title = nowWatchingInput.value.trim();
        }
        if (body.frame_b64 === undefined && currentFrameB64) {
          body.frame_b64 = currentFrameB64;
        }
        opts.body = JSON.stringify(body);
      }
    } catch (e) { /* leave untouched */ }
    return _origFetch.call(this, url, opts);
  };

})();
