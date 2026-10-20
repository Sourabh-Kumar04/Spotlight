/**
 * SPOTLIGHT — Phone Remote Client Script
 * Powers the tactile Curiosity Remote mobile web interface.
 */

(function () {
  const askBtn = document.getElementById("askBtn");
  const questionInput = document.getElementById("questionInput");
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

  let currentBeat = "kids";
  let scenesData = {};
  let ws = null;
  let isAsking = false;

  // Beat default questions map
  const defaultQuestions = {
    kids: "Why is the sky blue?",
    movie: "Who is that guy and why is everyone mad at him?",
    sports: "Why was that a foul?",
    news: "Is that claim true?",
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
    setAskButtonState(true);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          beat_id: currentBeat,
          question: question,
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
        await fetch("/api/reset", { method: "POST" });
        await loadHistory();
      } catch (err) {
        console.error("[Remote] Reset error", err);
      }
    });
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
})();
