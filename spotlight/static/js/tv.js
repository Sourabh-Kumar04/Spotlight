/**
 * SPOTLIGHT — Fire TV Client Script
 * Handles real-time freeze, analysis HUD, and big-type answer overlay.
 */

(function () {
  const container = document.getElementById("tvApp");
  const timecodeEl = document.getElementById("hudTimecode");
  const titleEl = document.getElementById("hudTitle");
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

  const scenesMap = {
    kids: sceneKids,
    movie: sceneMovie,
    sports: sceneSports,
    news: sceneNews,
  };

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

    if (scene) {
      if (titleEl) titleEl.textContent = scene.title;
      if (channelEl) channelEl.textContent = scene.channel;
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
  }

  // Keyboard controls for Fire TV testing
  window.addEventListener("keydown", async (e) => {
    // Space or Enter dismisses overlay or unfreezes
    if (e.code === "Space" || e.code === "Enter") {
      e.preventDefault();
      if (currentState.is_frozen) {
        await fetch("/api/dismiss", { method: "POST" });
      }
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

  // Initialize
  connectWS();
})();
