/**
 * SPOTLIGHT — Fire TV Client Script
 * Handles real-time freeze, analysis HUD, and big-type answer overlay.
 */

(function () {
  const container = document.getElementById("tvApp");
  const timecodeEl = document.getElementById("hudTimecode");
  const titleEl = document.getElementById("hudTitle");
  const contextTitleEl = document.getElementById("hudContextTitle");
  const channelEl = document.getElementById("hudChannel");
  const sceneLabelEl = document.getElementById("sceneLabel");

  // Overlay elements
  const overlayTitle = document.getElementById("overlayTitle");
  const overlaySubtitle = document.getElementById("overlaySubtitle");
  const overlayBadge = document.getElementById("overlayBadge");
  const overlayQuestion = document.getElementById("overlayQuestion");
  const overlayExplanation = document.getElementById("overlayExplanation");
  const overlayDetails = document.getElementById("overlayDetails");
  const overlaySources = document.getElementById("overlaySources");
  const overlayCompanion = document.getElementById("overlayCompanion");

  // Scenes
  const sceneKids = document.getElementById("sceneKids");
  const sceneMovie = document.getElementById("sceneMovie");
  const sceneSports = document.getElementById("sceneSports");
  const sceneNews = document.getElementById("sceneNews");
  const movieVideo = document.getElementById("movieVideo");

  const scenesMap = {
    kids: sceneKids,
    movie: sceneMovie,
    sports: sceneSports,
    news: sceneNews,
  };

  // ---- Spoken answers (Web Speech API) ----
  // The TV speaks the answer aloud; text overlay stays as visual support.
  let soundOn = true;
  let preferredVoice = null;

  function pickVoice() {
    try {
      const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
      if (!voices.length) return;
      preferredVoice =
        voices.find((v) => /google us english/i.test(v.name)) ||
        voices.find((v) => /^en[-_]US/i.test(v.lang)) ||
        voices.find((v) => /^en/i.test(v.lang)) ||
        voices[0];
    } catch (_) {}
  }
  if (window.speechSynthesis) {
    pickVoice();
    window.speechSynthesis.onvoiceschanged = pickVoice;
  }

  function stopSpeech() {
    try {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    } catch (_) {}
  }

  function speakAnswer(answer) {
    if (!soundOn || !window.speechSynthesis || !answer) return;
    stopSpeech();
    const text = `${answer.title || ""}. ${answer.primary_explanation || ""}`.trim();
    if (!text) return;
    const utter = new SpeechSynthesisUtterance(text);
    if (preferredVoice) utter.voice = preferredVoice;
    utter.rate = 1.0;
    utter.pitch = 1.0;

    utter.onstart = () => {
      setVoiceState("speaking", text.slice(0, 60) + (text.length > 60 ? "..." : ""), 10);
    };

    utter.onboundary = (e) => {
      if (e.charIndex && text.length) {
        const pct = Math.min(100, Math.round((e.charIndex / text.length) * 100));
        updateSpeakingProgress(pct);
      }
    };

    utter.onend = () => {
      updateSpeakingProgress(100);
      setTimeout(() => setVoiceState("idle"), 400);
    };

    utter.onerror = () => {
      setVoiceState("idle");
    };

    window.speechSynthesis.speak(utter);
    updateSoundBadge();
  }

  function toggleSound() {
    soundOn = !soundOn;
    if (!soundOn) stopSpeech();
    updateSoundBadge();
  }

  // --- Voice Status Pill (Extended from Sound Pill) ---
  // 4 states: listening (pulsing + live transcript), thinking (question), speaking (answer text + progress), idle.
  let soundBadge = null;
  let voicePillIndicator = null;
  let voicePillText = null;
  let voicePillProgress = null;
  let currentVoiceState = "idle";
  let speakingProgressInterval = null;

  function updateSoundBadge() {
    if (!soundBadge) {
      soundBadge = document.createElement("button");
      soundBadge.id = "soundToggle";
      soundBadge.className = "voice-status-pill voice-idle";

      voicePillIndicator = document.createElement("span");
      voicePillIndicator.className = "voice-pill-indicator";

      voicePillText = document.createElement("span");
      voicePillText.className = "voice-pill-text";

      voicePillProgress = document.createElement("span");
      voicePillProgress.className = "voice-pill-progress";
      voicePillProgress.style.width = "0%";

      soundBadge.appendChild(voicePillIndicator);
      soundBadge.appendChild(voicePillText);
      soundBadge.appendChild(voicePillProgress);

      soundBadge.addEventListener("click", () => {
        if (currentVoiceState === "idle") {
          toggleSound();
        }
      });
      document.body.appendChild(soundBadge);
    }
    renderVoicePillUI();
  }

  function setVoiceState(state, transcript, progressPct) {
    currentVoiceState = state || "idle";
    renderVoicePillUI(transcript, progressPct);
  }

  function updateSpeakingProgress(pct) {
    if (voicePillProgress) {
      voicePillProgress.style.width = `${Math.min(100, Math.max(0, pct))}%`;
    }
  }

  function renderVoicePillUI(transcript, progressPct) {
    if (!soundBadge) return;

    soundBadge.classList.remove("voice-idle", "voice-listening", "voice-thinking", "voice-speaking");
    soundBadge.classList.add(`voice-${currentVoiceState}`);

    if (speakingProgressInterval) {
      clearInterval(speakingProgressInterval);
      speakingProgressInterval = null;
    }

    if (currentVoiceState === "listening") {
      updateSpeakingProgress(0);
      const text = transcript ? `LISTENING: "${transcript}"` : "LISTENING...";
      voicePillText.textContent = text;
    } else if (currentVoiceState === "thinking") {
      updateSpeakingProgress(0);
      const text = transcript ? `THINKING: "${transcript}"` : "THINKING...";
      voicePillText.textContent = text;
    } else if (currentVoiceState === "speaking") {
      const text = transcript ? `SPEAKING: "${transcript}"` : "SPEAKING...";
      voicePillText.textContent = text;
      const initialPct = typeof progressPct === "number" ? progressPct : 15;
      updateSpeakingProgress(initialPct);

      if (typeof progressPct !== "number") {
        let pct = initialPct;
        speakingProgressInterval = setInterval(() => {
          pct = Math.min(95, pct + 5);
          updateSpeakingProgress(pct);
        }, 300);
      }
    } else {
      // idle state
      currentVoiceState = "idle";
      updateSpeakingProgress(0);
      voicePillText.textContent = soundOn ? "SOUND: ON" : "SOUND: OFF";
    }
  }
  updateSoundBadge();

  let currentState = {
    current_beat: "kids",
    status: "playing",
    is_frozen: false,
    current_overlay: null,
  };

  // WebSocket Setup
  let ws = null;
  function connectWS() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("[Spotlight TV] Connected to event hub");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleServerEvent(data);
      } catch (err) {
        console.error("[Spotlight TV] Parse error", err);
      }
    };

    ws.onclose = () => {
      console.log("[Spotlight TV] Disconnected. Reconnecting in 1.5s...");
      setTimeout(connectWS, 1500);
    };

    ws.onerror = (err) => {
      console.error("[Spotlight TV] WS Error", err);
      ws.close();
    };
  }

  function handleServerEvent(event) {
    console.log("[Spotlight TV] Event:", event.type, event);

    if (event.state) {
      applyState(event.state, event.scene);
    }

    if (event.type === "FREEZE") {
      setFreezeVisuals(true, "analyzing");
    } else if (event.type === "ANSWER") {
      setFreezeVisuals(true, "answered");
      if (event.answer) {
        renderOverlay(event.answer);
      }
    } else if (event.type === "UNFREEZE" || event.type === "RESET") {
      setFreezeVisuals(false, "playing");
    } else if (event.type === "BEAT_CHANGE") {
      setFreezeVisuals(false, "playing");
    }
  }

  function applyState(state, scene) {
    currentState = state;

    // Update scene view
    Object.keys(scenesMap).forEach((beat) => {
      const el = scenesMap[beat];
      if (el) {
        el.style.display = beat === state.current_beat ? "block" : "none";
      }
    });

    if (movieVideo) {
      if (state.current_beat === "movie" && !state.is_frozen) {
        movieVideo.play().catch(() => {});
      } else {
        movieVideo.pause();
      }
    }

    if (scene) {
      if (titleEl) titleEl.textContent = scene.title;
      if (contextTitleEl) {
        if (state && state.context_title) {
          contextTitleEl.textContent = `— ${state.context_title}`;
          contextTitleEl.style.display = "inline";
        } else {
          contextTitleEl.textContent = "";
          contextTitleEl.style.display = "none";
        }
      }
      if (channelEl) channelEl.textContent = scene.subtitle || scene.channel;
      if (sceneLabelEl) sceneLabelEl.textContent = `${scene.category.toUpperCase()} // ${scene.timestamp}`;
    }

    if (timecodeEl && state.timestamp) {
      timecodeEl.textContent = state.timestamp;
    }

    // Status classes
    setFreezeVisuals(state.is_frozen, state.status);

    if (state.current_overlay && state.status === "answered") {
      renderOverlay(state.current_overlay);
    }
  }

  function setFreezeVisuals(isFrozen, status) {
    container.classList.toggle("is-frozen", Boolean(isFrozen));
    container.classList.toggle("is-analyzing", status === "analyzing");
    container.classList.toggle("is-answered", status === "answered");

    if (movieVideo && currentState.current_beat === "movie") {
      if (isFrozen) {
        movieVideo.pause();
      } else {
        movieVideo.play().catch(() => {});
      }
    }
  }

  function renderOverlay(answer) {
    if (!answer) return;

    if (overlayTitle) overlayTitle.textContent = answer.title;
    if (overlaySubtitle) overlaySubtitle.textContent = answer.subtitle || "SPOTLIGHT KNOWLEDGE OVERLAY";
    if (overlayQuestion) overlayQuestion.textContent = `Q: ${answer.question}`;
    if (overlayExplanation) overlayExplanation.textContent = answer.primary_explanation;

    // Badge
    if (overlayBadge) {
      if (answer.verdict_badge) {
        overlayBadge.style.display = "inline-flex";
        overlayBadge.textContent = answer.verdict_badge;
        overlayBadge.className = `badge badge-${answer.verdict_color || "sky"}`;
      } else {
        overlayBadge.style.display = "none";
      }
    }

    // Key details
    if (overlayDetails) {
      overlayDetails.innerHTML = "";
      if (Array.isArray(answer.key_details) && answer.key_details.length > 0) {
        answer.key_details.forEach((item) => {
          const card = document.createElement("div");
          card.className = "detail-card";
          card.textContent = item;
          overlayDetails.appendChild(card);
        });
      }
    }

    // Sources
    if (overlaySources) {
      overlaySources.innerHTML = "";
      if (Array.isArray(answer.sources) && answer.sources.length > 0) {
        answer.sources.forEach((src) => {
          const span = document.createElement("span");
          span.className = "source-item";
          span.textContent = src;
          overlaySources.appendChild(span);
        });
      }
    }

    // Companion seed
    if (overlayCompanion) {
      if (answer.companion_note) {
        overlayCompanion.style.display = "inline-block";
        overlayCompanion.textContent = answer.companion_note;
      } else {
        overlayCompanion.style.display = "none";
      }
    }

    // Spoken reply
    speakAnswer(answer);
  }

  // Keyboard controls for Fire TV testing
  window.addEventListener("keydown", async (e) => {
    // Space or Enter dismisses overlay or unfreezes
    if (e.code === "Space" || e.code === "Enter") {
      e.preventDefault();
      stopSpeech();
      if (currentState.is_frozen) {
        await fetch("/api/dismiss", { method: "POST" });
      }
    } else if (e.key === "m" || e.key === "M") {
      toggleSound();
    } else if (e.key === "1") {
      await fetch("/api/beat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ beat_id: "kids" }),
      });
    } else if (e.key === "2") {
      await fetch("/api/beat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ beat_id: "movie" }),
      });
    } else if (e.key === "3") {
      await fetch("/api/beat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ beat_id: "sports" }),
      });
    } else if (e.key === "4") {
      await fetch("/api/beat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ beat_id: "news" }),
      });
    }
  });

  // Polling fallback to guarantee state sync if WebSocket is blocked
  setInterval(async () => {
    try {
      const res = await fetch("/api/state");
      if (res.ok) {
        const data = await res.json();
        applyState(data.state, data.scene);
      }
    } catch (_) {}
  }, 2500);

  // --- Session-Isolated WebSocket Hub (/ws/session/{session_id}) ---
  // Subscribes to /remote voice_state updates and control commands.
  let sessionWs = null;
  const sessionId = new URLSearchParams(window.location.search).get("session") || "default";

  function connectSessionWS() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const hubUrl = `${protocol}//${window.location.host}/ws/session/${sessionId}`;

    sessionWs = new WebSocket(hubUrl);

    sessionWs.onopen = () => {
      console.log(`[Spotlight TV] Connected to session hub: ${sessionId}`);
    };

    sessionWs.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleSessionMessage(msg);
      } catch (err) {
        console.error("[Spotlight TV] Session hub parse error", err);
      }
    };

    sessionWs.onclose = () => {
      console.log("[Spotlight TV] Session hub disconnected. Reconnecting in 1.5s...");
      setTimeout(connectSessionWS, 1500);
    };

    sessionWs.onerror = (err) => {
      console.error("[Spotlight TV] Session hub error", err);
      sessionWs.close();
    };
  }

  function handleSessionMessage(msg) {
    if (!msg || !msg.kind) return;

    if (msg.kind === "voice_state") {
      const state = (msg.state || "idle").toLowerCase();
      setVoiceState(state, msg.transcript);
    } else if (msg.kind === "control") {
      executeControl(msg);
    }
  }

  // IMPORTANT: NO ADB — this demo runs against a cloud Fire TV the backend cannot reach;
  // web-page control is the correct substrate.
  function executeControl(msg) {
    console.log("[Spotlight TV] Executing web-page device control:", msg);
    const video = document.querySelector("video") || movieVideo;
    const action = (msg.action || "").toLowerCase();
    const seconds = Number(msg.seconds) || 10;

    if (action === "pause") {
      if (video) video.pause();
    } else if (action === "play" || action === "resume") {
      if (video) video.play().catch(() => {});
      if (currentState.is_frozen) {
        fetch("/api/dismiss", { method: "POST" }).catch(() => {});
      }
    } else if (action === "rewind") {
      if (video) {
        video.currentTime = Math.max(0, (video.currentTime || 0) - seconds);
      }
    } else if (action === "forward") {
      if (video) {
        video.currentTime = Math.min(video.duration || 999999, (video.currentTime || 0) + seconds);
      }
    } else if (action === "volume_up" || action === "volume-up") {
      if (video) {
        video.muted = false;
        video.volume = Math.min(1.0, Number(((video.volume || 1.0) + 0.1).toFixed(2)));
      }
    } else if (action === "volume_down" || action === "volume-down") {
      if (video) {
        video.volume = Math.max(0.0, Number(((video.volume || 1.0) - 0.1).toFixed(2)));
      }
    } else if (action === "mute") {
      if (video) {
        video.muted = !video.muted;
      }
      toggleSound();
    } else if (action === "go-back" || action === "go_back" || action === "back") {
      if (currentState.is_frozen || currentState.status === "answered") {
        stopSpeech();
        fetch("/api/dismiss", { method: "POST" }).catch(() => {});
      }
    }
  }

  // Initialize
  connectWS();
  connectSessionWS();
})();
