(function () {
  const audio = document.getElementById("audio");
  const wavSelect = document.getElementById("wav-select");
  const btnPlayPause = document.getElementById("btn-play-pause");
  const seek = document.getElementById("seek");
  const timeCurrent = document.getElementById("time-current");
  const timeTotal = document.getElementById("time-total");
  const sceneSelect = document.getElementById("scene-select");
  const beatCounter = document.getElementById("beat-counter");
  const beatCountEl = document.getElementById("beat-count");
  const recordFeedback = document.getElementById("record-feedback");

  const API = "/api";

  function setFeedback(msg, isError) {
    recordFeedback.textContent = msg;
    recordFeedback.className = "feedback " + (isError ? "error" : "success");
  }

  function clearFeedback() {
    recordFeedback.textContent = "";
    recordFeedback.className = "feedback";
  }

  async function loadWavList() {
    try {
      const res = await fetch(API + "/wav-files");
      const files = await res.json();
      wavSelect.innerHTML = "";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "-- 請選擇 --";
      wavSelect.appendChild(empty);
      files.forEach(function (name) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        wavSelect.appendChild(opt);
      });
    } catch (e) {
      wavSelect.innerHTML = "<option value=''>載入失敗</option>";
    }
  }

  wavSelect.addEventListener("change", function () {
    const file = wavSelect.value;
    if (!file) {
      audio.removeAttribute("src");
      audio.load();
      seek.max = 100;
      seek.value = 0;
      timeCurrent.textContent = "0.000";
      timeTotal.textContent = "0.000";
      return;
    }
    audio.src = API + "/audio/" + encodeURIComponent(file);
    audio.load();
  });

  audio.addEventListener("loadedmetadata", function () {
    const d = audio.duration;
    if (Number.isFinite(d)) {
      seek.max = d;
      seek.value = 0;
      timeTotal.textContent = d.toFixed(3);
    }
  });

  audio.addEventListener("timeupdate", function () {
    const t = audio.currentTime;
    if (!seek.dragging) {
      seek.value = t;
      timeCurrent.textContent = t.toFixed(3);
    }
  });

  audio.addEventListener("ended", function () {
    seek.value = 0;
    timeCurrent.textContent = "0.000";
  });

  let seekDragging = false;
  Object.defineProperty(seek, "dragging", { get: function () { return seekDragging; }, set: function (v) { seekDragging = v; }, configurable: true });

  seek.addEventListener("mousedown", function () { seekDragging = true; });
  seek.addEventListener("mouseup", function () { seekDragging = false; });
  seek.addEventListener("input", function () {
    const t = parseFloat(seek.value);
    if (Number.isFinite(t)) {
      audio.currentTime = t;
      timeCurrent.textContent = t.toFixed(3);
    }
  });

  function updatePlayPauseButton() {
    if (!audio.paused) {
      btnPlayPause.textContent = "⏸ 暫停";
      btnPlayPause.setAttribute("aria-label", "暫停");
    } else {
      btnPlayPause.textContent = "▶ 播放";
      btnPlayPause.setAttribute("aria-label", "播放");
    }
  }

  btnPlayPause.addEventListener("click", function () {
    if (!audio.src) return;
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  });
  audio.addEventListener("play", updatePlayPauseButton);
  audio.addEventListener("pause", updatePlayPauseButton);
  updatePlayPauseButton();

  async function loadSceneList() {
    try {
      const res = await fetch(API + "/scenes");
      const list = await res.json();
      sceneSelect.innerHTML = "";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "-- 請選擇 scene --";
      sceneSelect.appendChild(empty);
      (list || []).forEach(function (name) {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        sceneSelect.appendChild(opt);
      });
    } catch (_) {
      sceneSelect.innerHTML = "<option value=''>載入失敗</option>";
    }
  }

  async function updateBeatCount() {
    const scene = sceneSelect.value ? sceneSelect.value.trim() : "";
    if (!scene) {
      beatCountEl.textContent = "0";
      return;
    }
    try {
      const res = await fetch(API + "/beats");
      const data = await res.json();
      const col = (data.headers || []).indexOf(scene);
      if (col === -1) {
        beatCountEl.textContent = "0";
        return;
      }
      let n = 0;
      (data.rows || []).forEach(function (row) {
        if (row[col] && row[col].trim() !== "") n++;
      });
      beatCountEl.textContent = String(n);
    } catch (_) {
      beatCountEl.textContent = "0";
    }
  }

  sceneSelect.addEventListener("change", updateBeatCount);

  beatCounter.addEventListener("click", async function () {
    const scene = sceneSelect.value ? sceneSelect.value.trim() : "";
    if (!scene) {
      setFeedback("請先選擇 Scene", true);
      return;
    }
    const t = audio.currentTime;
    const timeStr = t.toFixed(3);
    try {
      const res = await fetch(API + "/beats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scene: scene, time: t }),
      });
      const result = await res.json();
      if (result.ok) {
        setFeedback("已記錄 " + scene + " 第 " + timeStr + " 秒");
        updateBeatCount();
        setTimeout(clearFeedback, 2500);
      } else {
        setFeedback(result.error || "寫入失敗", true);
      }
    } catch (e) {
      setFeedback("網路錯誤", true);
    }
  });

  loadWavList();
  loadSceneList();
})();
