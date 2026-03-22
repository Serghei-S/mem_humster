const startButton = document.querySelector("#startButton");
const statusBadge = document.querySelector("#statusBadge");
const faceBadge = document.querySelector("#faceBadge");
const analysisBadge = document.querySelector("#analysisBadge");
const expressionBadge = document.querySelector("#expressionBadge");
const video = document.querySelector("#camera");
const canvas = document.querySelector("#captureCanvas");
const bestImage = document.querySelector("#bestImage");
const bestFile = document.querySelector("#bestFile");
const bestLabel = document.querySelector("#bestLabel");
const bestDescription = document.querySelector("#bestDescription");
const bestScore = document.querySelector("#bestScore");
const hamsterTraits = document.querySelector("#hamsterTraits");
const alternatives = document.querySelector("#alternatives");
const gallery = document.querySelector("#gallery");
const meterValue = document.querySelector("#meterValue");
const meterFill = document.querySelector("#meterFill");
const verdictLine = document.querySelector("#verdictLine");
const historyRail = document.querySelector("#historyRail");
const faceReadout = document.querySelector("#faceReadout");
const featureGrid = document.querySelector("#featureGrid");
const scoreBreakdown = document.querySelector("#scoreBreakdown");

const ctx = canvas.getContext("2d", { willReadFrequently: true });

const MEDIAPIPE_BUNDLE_URL =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs";
const MEDIAPIPE_WASM_ROOT =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const FACE_MODEL_URL = "/static/models/face_landmarker.task";

let analyzeTimer = null;
let faceLoopHandle = null;
let busy = false;
let stream = null;
let historyMatches = [];
let faceLandmarker = null;
let faceModulePromise = null;
let landmarkerLoading = null;
let landmarkerReady = false;
let landmarkerError = null;
let latestFaceFeatures = null;
let latestFaceSeenAt = 0;
let lastVideoTime = -1;
let lastLandmarkAt = 0;

function setStatus(text, tone = "loading") {
  statusBadge.textContent = text;
  statusBadge.className = `status-badge ${tone}`;
}

function setPanelPill(target, text, tone = "waiting") {
  target.textContent = text;
  target.className = `panel-pill ${tone}`;
}

function updateFaceBadge() {
  if (landmarkerError) {
    setPanelPill(faceBadge, "Геометрия лица недоступна", "warning");
    return;
  }

  if (latestFaceFeatures && landmarkerReady) {
    setPanelPill(faceBadge, "Читаю рот, глаза и брови", "ready");
    return;
  }

  if (stream && landmarkerReady) {
    setPanelPill(faceBadge, "Жду устойчивое лицо в кадре", "waiting");
    return;
  }

  if (landmarkerLoading) {
    setPanelPill(faceBadge, "Загружаю анализ лица", "waiting");
    return;
  }

  setPanelPill(faceBadge, "Готовлю анализ лица", "waiting");
}

function renderChips(target, items, emptyText = "") {
  target.innerHTML = "";

  if (!items.length && emptyText) {
    const chip = document.createElement("span");
    chip.className = "chip ghost";
    chip.textContent = emptyText;
    target.appendChild(chip);
    return;
  }

  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent =
      typeof item === "string" ? item : `${item.label} ${Math.round(item.score * 100)}%`;
    target.appendChild(chip);
  });
}

function renderFeatureGrid(items) {
  featureGrid.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "feature-empty";
    empty.textContent = "Пока не вижу достаточно стабильное лицо для геометрии.";
    featureGrid.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "feature-card";
    card.innerHTML = `
      <div class="feature-copy">
        <span>${item.label}</span>
        <strong>${Math.round(item.score * 100)}%</strong>
      </div>
      <div class="feature-track">
        <div class="feature-fill" style="width: ${Math.max(4, Math.round(item.score * 100))}%"></div>
      </div>
    `;
    featureGrid.appendChild(card);
  });
}

function renderScoreBreakdown(breakdown, analysisMode) {
  scoreBreakdown.innerHTML = "";

  if (!breakdown) {
    return;
  }

  const entries =
    analysisMode === "face_geometry"
      ? [
          ["face_geometry", "Лицо"],
          ["semantic", "Мимика"],
          ["description", "Описание"],
        ]
      : [
          ["semantic", "Мимика"],
          ["description", "Описание"],
          ["visual", "Кадр"],
        ];

  entries.forEach(([key, label]) => {
    if (typeof breakdown[key] !== "number") {
      return;
    }

    const badge = document.createElement("span");
    badge.className = "breakdown-pill";
    badge.textContent = `${label} ${Math.round(breakdown[key] * 100)}%`;
    scoreBreakdown.appendChild(badge);
  });
}

function buildVerdict(score, label, analysisMode) {
  if (analysisMode !== "face_geometry") {
    return "Геометрию лица пока не вижу, поэтому это только мягкое совпадение по общему кадру.";
  }

  if (score >= 0.9) {
    return `Очень близко по мимике. Сейчас лицо больше всего похоже на "${label.toLowerCase()}".`;
  }

  if (score >= 0.82) {
    return "Хорошее совпадение по рту, глазам и бровям. Сервис уже опирается именно на лицо.";
  }

  if (score >= 0.72) {
    return "Совпадение заметное, но не идеальное. Поза лица считывается, просто похожих хомяков рядом несколько.";
  }

  return "Лицо считываю, но совпадение пока мягкое. Попробуй сильнее открыть рот, улыбнуться или нахмуриться.";
}

function renderHistory() {
  historyRail.innerHTML = "";
  historyMatches.forEach((item) => {
    const card = document.createElement("article");
    card.className = "history-card";
    card.innerHTML = `
      <img src="${item.image_url}" alt="${item.label}" />
      <div>
        <strong>${item.label}</strong>
        <span>${item.scoreText}</span>
      </div>
    `;
    historyRail.appendChild(card);
  });
}

function pushHistory(bestMatch) {
  const entry = {
    filename: bestMatch.filename,
    label: bestMatch.label,
    image_url: bestMatch.image_url,
    scoreText: `${Math.round(bestMatch.score * 100)}%`,
  };

  const last = historyMatches[0];
  if (last && last.filename === entry.filename) {
    historyMatches[0] = entry;
  } else {
    historyMatches.unshift(entry);
  }

  historyMatches = historyMatches.slice(0, 6);
  renderHistory();
}

function renderGallery(referenceItems) {
  gallery.innerHTML = "";
  referenceItems.forEach((item) => {
    const card = document.createElement("article");
    card.className = "gallery-card";
    card.innerHTML = `
      <img src="${item.image_url}" alt="${item.filename}" />
      <div class="gallery-copy">
        <strong>${item.label}</strong>
        <span class="gallery-file">${item.filename}</span>
        <p>${item.description}</p>
        <div class="chips-row gallery-traits">
          ${item.traits.map((trait) => `<span class="chip">${trait}</span>`).join("")}
        </div>
      </div>
    `;
    gallery.appendChild(card);
  });
}

function renderAlternatives(items) {
  alternatives.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("article");
    row.className = "alternative-card";
    row.innerHTML = `
      <img src="${item.image_url}" alt="${item.filename}" />
      <div>
        <strong>${item.label}</strong>
        <p>${item.description}</p>
        <div class="chips-row alt-traits">
          ${item.traits.slice(0, 3).map((trait) => `<span class="chip">${trait}</span>`).join("")}
        </div>
      </div>
      <span>${Math.round(item.score * 100)}%</span>
    `;
    alternatives.appendChild(row);
  });
}

function renderMatch(result) {
  const {
    best_match: bestMatch,
    alternatives: alternativeItems,
    analysis_mode: analysisMode,
    current_expression: currentExpression,
    current_features: currentFeatures,
    face_geometry_found: faceGeometryFound,
  } = result;

  bestImage.src = bestMatch.image_url;
  bestFile.textContent = bestMatch.filename;
  bestLabel.textContent = bestMatch.label;
  bestDescription.textContent = bestMatch.description;
  bestScore.textContent =
    analysisMode === "face_geometry"
      ? `Совпадение по лицу: ${Math.round(bestMatch.score * 100)}%`
      : `Похожесть по кадру: ${Math.round(bestMatch.score * 100)}%`;
  meterValue.textContent = `${Math.round(bestMatch.score * 100)}%`;
  meterFill.style.width = `${Math.max(8, Math.round(bestMatch.score * 100))}%`;
  verdictLine.textContent = buildVerdict(bestMatch.score, bestMatch.label, analysisMode);
  expressionBadge.textContent =
    analysisMode === "face_geometry"
      ? `По лицу ближе всего: ${bestMatch.label}`
      : `Временный fallback: ${bestMatch.label}`;

  if (faceGeometryFound) {
    setPanelPill(analysisBadge, "Матчинг по геометрии лица", "ready");
  } else if (landmarkerError) {
    setPanelPill(analysisBadge, "Без геометрии, только кадр", "warning");
  } else {
    setPanelPill(analysisBadge, "Жду устойчивое лицо для геометрии", "waiting");
  }

  renderChips(hamsterTraits, bestMatch.traits, "Черты хомяка появятся после первого кадра");
  renderChips(faceReadout, currentExpression, "Жду читаемую мимику");
  renderFeatureGrid(currentFeatures);
  renderScoreBreakdown(bestMatch.score_breakdown, analysisMode);
  renderAlternatives(alternativeItems);
  pushHistory(bestMatch);
  updateFaceBadge();
}

async function loadReferences() {
  const response = await fetch("/api/references");
  if (!response.ok) {
    throw new Error("Не удалось загрузить список хомяков");
  }

  const payload = await response.json();
  renderGallery(payload.references);
  renderChips(faceReadout, [], "Жду лицо в кадре");
  renderFeatureGrid([]);

  if (payload.references[0]) {
    bestImage.src = payload.references[0].image_url;
    bestFile.textContent = payload.references[0].filename;
    bestLabel.textContent = payload.references[0].label;
    bestDescription.textContent = payload.references[0].description;
    bestScore.textContent = "Совпадение появится после первого кадра";
    verdictLine.textContent =
      "Включи камеру, и сервис начнет сопоставлять твое лицо с хомяками по геометрии выражения.";
    renderChips(hamsterTraits, payload.references[0].traits);
  }
}

function clamp(value) {
  return Math.max(0, Math.min(1, value));
}

function averageBlendshape(scores, names) {
  if (!names.length) {
    return 0;
  }
  return names.reduce((sum, name) => sum + (scores[name] || 0), 0) / names.length;
}

function extractFaceFeatures(categories) {
  if (!categories?.length) {
    return null;
  }

  const blendshapes = Object.fromEntries(
    categories.map((item) => [item.categoryName, item.score]),
  );

  const blink = averageBlendshape(blendshapes, ["eyeBlinkLeft", "eyeBlinkRight"]);
  const wide = averageBlendshape(blendshapes, ["eyeWideLeft", "eyeWideRight"]);
  const squint = averageBlendshape(blendshapes, ["eyeSquintLeft", "eyeSquintRight"]);

  const features = {
    mouth_open: clamp(
      (blendshapes.jawOpen || 0) * 0.82 +
        averageBlendshape(blendshapes, ["mouthLowerDownLeft", "mouthLowerDownRight"]) * 0.32 +
        averageBlendshape(blendshapes, ["mouthUpperUpLeft", "mouthUpperUpRight"]) * 0.18,
    ),
    mouth_round: clamp(
      averageBlendshape(blendshapes, ["mouthPucker", "mouthFunnel"]) * 1.15,
    ),
    smile: clamp(
      averageBlendshape(blendshapes, ["mouthSmileLeft", "mouthSmileRight"]) * 0.9 +
        averageBlendshape(blendshapes, ["mouthDimpleLeft", "mouthDimpleRight"]) * 0.25,
    ),
    sadness: clamp(
      averageBlendshape(blendshapes, ["mouthFrownLeft", "mouthFrownRight"]) * 1.05 +
        (blendshapes.browInnerUp || 0) * 0.22,
    ),
    eye_open: clamp((1 - blink) * 0.3 + wide * 1.0 - squint * 0.2),
    brow_raise: clamp(
      ((blendshapes.browInnerUp || 0) * 0.6 +
        averageBlendshape(blendshapes, ["browOuterUpLeft", "browOuterUpRight"]) * 0.4) *
        1.1,
    ),
    brow_frown: clamp(
      averageBlendshape(blendshapes, ["browDownLeft", "browDownRight"]) * 1.15,
    ),
    asymmetry: clamp(
      Math.max(
        Math.abs((blendshapes.mouthSmileLeft || 0) - (blendshapes.mouthSmileRight || 0)),
        Math.abs((blendshapes.mouthFrownLeft || 0) - (blendshapes.mouthFrownRight || 0)),
        Math.abs((blendshapes.eyeWideLeft || 0) - (blendshapes.eyeWideRight || 0)),
        Math.abs((blendshapes.browOuterUpLeft || 0) - (blendshapes.browOuterUpRight || 0)),
        Math.abs((blendshapes.mouthStretchLeft || 0) - (blendshapes.mouthStretchRight || 0)),
      ) * 1.65,
    ),
  };

  if (Math.max(...Object.values(features)) < 0.03) {
    return null;
  }

  return Object.fromEntries(
    Object.entries(features).map(([name, value]) => [name, Number(value.toFixed(4))]),
  );
}

function currentFaceFeaturesForRequest() {
  if (!latestFaceFeatures) {
    return null;
  }

  if (performance.now() - latestFaceSeenAt > 2200) {
    return null;
  }

  return { ...latestFaceFeatures };
}

async function analyzeFrame() {
  if (busy || !stream) {
    return;
  }

  busy = true;
  const width = video.videoWidth || 640;
  const height = video.videoHeight || 480;
  canvas.width = width;
  canvas.height = height;
  ctx.drawImage(video, 0, 0, width, height);

  try {
    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image: canvas.toDataURL("image/jpeg", 0.88),
        face_features: currentFaceFeaturesForRequest(),
      }),
    });

    if (!response.ok) {
      throw new Error("Модель не смогла обработать кадр");
    }

    const payload = await response.json();
    renderMatch(payload);
    setStatus("Камера активна", "ready");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    busy = false;
  }
}

async function loadFaceModule() {
  if (!faceModulePromise) {
    faceModulePromise = import(MEDIAPIPE_BUNDLE_URL);
  }

  return faceModulePromise;
}

async function createFaceLandmarker(delegate) {
  const { FaceLandmarker, FilesetResolver } = await loadFaceModule();
  const filesetResolver = await FilesetResolver.forVisionTasks(MEDIAPIPE_WASM_ROOT);
  return FaceLandmarker.createFromOptions(filesetResolver, {
    baseOptions: {
      modelAssetPath: FACE_MODEL_URL,
      delegate,
    },
    runningMode: "VIDEO",
    numFaces: 1,
    outputFaceBlendshapes: true,
    minFaceDetectionConfidence: 0.45,
    minFacePresenceConfidence: 0.45,
    minTrackingConfidence: 0.45,
  });
}

async function initFaceLandmarker() {
  if (landmarkerReady) {
    return faceLandmarker;
  }

  if (landmarkerLoading) {
    return landmarkerLoading;
  }

  updateFaceBadge();
  landmarkerLoading = (async () => {
    try {
      try {
        faceLandmarker = await createFaceLandmarker("GPU");
      } catch (gpuError) {
        faceLandmarker = await createFaceLandmarker("CPU");
      }
      landmarkerReady = true;
      landmarkerError = null;
      return faceLandmarker;
    } catch (error) {
      landmarkerError = error;
      throw error;
    } finally {
      landmarkerLoading = null;
      updateFaceBadge();
    }
  })();

  return landmarkerLoading;
}

function readFaceFromVideo(now) {
  if (!faceLandmarker || video.readyState < 2) {
    return;
  }

  try {
    const result = faceLandmarker.detectForVideo(video, now);
    const features = extractFaceFeatures(result.faceBlendshapes?.[0]?.categories || []);
    latestFaceFeatures = features;
    latestFaceSeenAt = features ? now : 0;
    updateFaceBadge();
  } catch (error) {
    landmarkerError = error;
    latestFaceFeatures = null;
    updateFaceBadge();
  }
}

function startFaceLoop() {
  if (faceLoopHandle) {
    return;
  }

  const tick = () => {
    const now = performance.now();
    if (
      stream &&
      faceLandmarker &&
      video.readyState >= 2 &&
      video.currentTime !== lastVideoTime &&
      now - lastLandmarkAt >= 120
    ) {
      lastVideoTime = video.currentTime;
      lastLandmarkAt = now;
      readFaceFromVideo(now);
    }
    faceLoopHandle = window.requestAnimationFrame(tick);
  };

  faceLoopHandle = window.requestAnimationFrame(tick);
}

async function startCamera() {
  if (stream) {
    return;
  }

  try {
    const landmarkerPromise = initFaceLandmarker().catch(() => null);

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    });

    video.srcObject = stream;
    await video.play();
    await landmarkerPromise;

    setStatus("Камера подключена", "ready");
    startButton.disabled = true;
    updateFaceBadge();
    startFaceLoop();
    analyzeTimer = window.setInterval(analyzeFrame, 850);
    analyzeFrame();
  } catch (error) {
    setStatus("Нужен доступ к камере в браузере", "error");
  }
}

startButton.addEventListener("click", startCamera);

window.addEventListener("beforeunload", () => {
  if (analyzeTimer) {
    window.clearInterval(analyzeTimer);
  }

  if (faceLoopHandle) {
    window.cancelAnimationFrame(faceLoopHandle);
  }

  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
});

loadReferences()
  .then(() => {
    updateFaceBadge();
    setPanelPill(analysisBadge, "Жду данные по лицу", "waiting");
    setStatus("Можно включать камеру", "ready");
    initFaceLandmarker().catch(() => {
      setPanelPill(analysisBadge, "Если геометрия не загрузится, будет fallback", "warning");
      updateFaceBadge();
    });
  })
  .catch((error) => setStatus(error.message, "error"));
