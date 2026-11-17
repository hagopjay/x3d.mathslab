/* Math Lab UI: the server owns mathematical samples and XML; this view consumes them.
   Requested controls, accepted model and displayed native scene are separate states.
   Exports stay disabled until the newest request is accepted. No code is evaluated. */
"use strict";
const $ = (id) => document.getElementById(id);
const NS = "http://www.w3.org/2000/svg";
const state = {
  lessons: [],
  lesson: null,
  params: {},
  accepted: null,
  revision: 0,
  controller: null,
  debounce: null,
  native: null,
  nativeReady: null,
  nativeFailed: false,
  projectionOnly: false,
  worldQueue: Promise.resolve(),
  story: 0,
  mode: "explore",
  playing: false,
  playToken: 0,
  reduced: false,
  toastTimer: null,
};
const shortNames = {
  linear: "Linear transformations",
  derivative: "The moving tangent",
  integral: "An area, assembled",
  fourier: "Circles into signals",
  lorenz: "The shape of chaos",
  gradient: "A path downhill",
};
const domains = {
  linear: "LINEAR ALGEBRA",
  derivative: "DIFFERENTIAL CALCULUS",
  integral: "INTEGRAL CALCULUS",
  fourier: "HARMONIC MOTION",
  lorenz: "DYNAMICAL SYSTEMS",
  gradient: "OPTIMIZATION",
};

const finite = (n) => typeof n === "number" && Number.isFinite(n);
function node(tag, cls, text) {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text !== undefined) el.textContent = text;
  return el;
}
function svg(tag, attrs = {}) {
  const el = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
  return el;
}
function message(text) {
  clearTimeout(state.toastTimer);
  $("toast").textContent = text;
  $("toast").classList.add("visible");
  state.toastTimer = setTimeout(
    () => $("toast").classList.remove("visible"),
    3200,
  );
}
function error(text) {
  $("errorNotice").hidden = !text;
  $("errorNotice").textContent = text || "";
}
function numeric(value) {
  if (!finite(value)) return String(value ?? "—");
  const a = Math.abs(value);
  if (a !== 0 && (a < 0.0001 || a >= 100000)) return value.toExponential(3);
  if (Number.isInteger(value)) return value.toLocaleString();
  return Number(value.toPrecision(5)).toLocaleString(undefined, {
    maximumFractionDigits: 7,
  });
}
function defaults(lesson) {
  return Object.fromEntries(lesson.parameters.map((p) => [p.id, p.default]));
}
function setBusy(busy) {
  $("stage").setAttribute("aria-busy", String(busy));
  $("metrics").classList.toggle("pending", busy);
  $("metrics").setAttribute("aria-busy", String(busy));
  if (busy && state.accepted)
    $("sourceMeta").textContent =
      "Previous accepted source shown · exports paused until the new parameters are accepted.";
  $("updateLabel").hidden = !busy || !state.accepted;
  for (const id of [
    "saveCard",
    "downloadX3D",
    "sourceDownload",
    "copySource",
    "downloadManim",
    "projectionToggle",
    "cameraReset",
  ])
    $(id).disabled = busy || !state.accepted;
}
function stopMotion() {
  state.playing = false;
  state.playToken++;
  $("animateParameter").textContent = "▶ Set it in motion";
  $("animateParameter").setAttribute("aria-pressed", "false");
}
function changePanel(id) {
  state.mode = id;
  for (const b of document.querySelectorAll("[data-panel]")) {
    const active = b.dataset.panel === id;
    b.setAttribute("aria-selected", String(active));
    b.tabIndex = active ? 0 : -1;
  }
  for (const panel of document.querySelectorAll(".bench-panel")) {
    const active = panel.id === "panel-" + id;
    panel.hidden = !active;
    panel.classList.toggle("active", active);
  }
}
function buildNav() {
  const nav = $("lessonNav");
  nav.replaceChildren();
  state.lessons.forEach((lesson, i) => {
    const b = node("button", "lesson-button");
    b.dataset.lesson = lesson.id;
    b.setAttribute("aria-current", "false");
    b.append(node("span", "n", String(i + 1).padStart(2, "0")));
    const text = node("span");
    text.append(
      node("strong", "", shortNames[lesson.id] || lesson.title),
      node("small", "", domains[lesson.id] || lesson.tagline),
    );
    b.append(text);
    b.onclick = () => choose(lesson.id);
    nav.append(b);
  });
}
function resetPrediction() {
  $("predictionText").value = "";
  $("challengeAnswer").hidden = true;
  $("revealAnswer").textContent = "Reveal the reasoning ↘";
}
function choose(id, incoming) {
  const lesson = state.lessons.find((l) => l.id === id);
  if (!lesson) throw new Error("That lesson is not in this collection.");
  stopMotion();
  clearTimeout(state.debounce);
  state.controller?.abort();
  state.revision++;
  state.accepted = null;
  state.lesson = lesson;
  state.params = incoming ? { ...incoming } : defaults(lesson);
  state.story = 0;
  error("");
  resetPrediction();
  document.documentElement.style.setProperty(
    "--accent",
    lesson.accent || "#65d9d2",
  );
  $("lessonTitle").textContent = lesson.title;
  $("lessonTagline").textContent = lesson.tagline || "";
  $("lessonDescription").textContent = lesson.description || "";
  $("lessonCategory").textContent = domains[id] || "A CONNECTED IDEA";
  $("lessonIndex").textContent = String(
    state.lessons.indexOf(lesson) + 1,
  ).padStart(2, "0");
  $("formula").textContent = lesson.formula || "";
  $("challengeQuestion").textContent =
    lesson.challenge?.question || "What changes when you change one parameter?";
  $("challengeAnswer").textContent =
    lesson.challenge?.answer ||
    "Try two parameter values, then compare the measured result.";
  for (const b of document.querySelectorAll("[data-lesson]"))
    b.setAttribute("aria-current", String(b.dataset.lesson === id));
  buildControls();
  buildStory();
  $("sourceText").value = "";
  $("metrics").replaceChildren();
  $("insights").replaceChildren();
  $("modelIdentity").textContent = "Recomputing this model…";
  $("sourceMeta").textContent = "Waiting for this experiment.";
  $("stageMessage").hidden = false;
  $("stageMessage").querySelector("span").textContent =
    "Finding the shape of an idea…";
  setBusy(true);
  history.replaceState(null, "", "#" + id);
  compute();
}
function buildControls() {
  const box = $("parameters");
  box.replaceChildren();
  for (const p of state.lesson.parameters) {
    const wrap = node("div", "parameter"),
      head = node("div", "parameter-head"),
      label = node("label", "", p.label);
    label.htmlFor = "range-" + p.id;
    const val = node("div", "parameter-value"),
      num = node("input");
    num.type = "number";
    num.id = "number-" + p.id;
    num.min = p.min;
    num.max = p.max;
    num.step = p.type === "integer" ? p.step : "any";
    num.value = state.params[p.id] ?? p.default;
    num.setAttribute("aria-label", p.label + " numeric value");
    val.append(num);
    if (p.unit) val.append(node("small", "", p.unit));
    head.append(label, val);
    const range = node("input");
    range.type = "range";
    range.id = "range-" + p.id;
    range.min = p.min;
    range.max = p.max;
    // Continuous controls preserve defaults such as β=8/3 and phase=2π exactly.
    range.step = p.type === "integer" ? p.step : "any";
    range.value = num.value;
    range.setAttribute("aria-label", p.label);
    const ends = node("div", "parameter-ends");
    ends.append(
      node("span", "", numeric(p.min)),
      node("span", "", numeric(p.max)),
    );
    wrap.append(head, range, ends);
    range.oninput = () => {
      num.value = range.value;
      state.params[p.id] = Number(range.value);
      schedule();
    };
    num.onchange = () => {
      const value = Number(num.value);
      if (
        !finite(value) ||
        value < p.min ||
        value > p.max ||
        (p.type === "integer" && !Number.isInteger(value))
      ) {
        num.setAttribute("aria-invalid", "true");
        error(
          p.label +
            " must be " +
            (p.type === "integer" ? "an integer" : "a number") +
            " from " +
            p.min +
            " to " +
            p.max +
            ".",
        );
        setBusy(true);
        state.revision++;
        state.controller?.abort();
        return;
      }
      num.removeAttribute("aria-invalid");
      range.value = String(value);
      state.params[p.id] = value;
      schedule();
    };
    box.append(wrap);
  }
  const animation = state.lesson.animation;
  $("animateParameter").hidden = !animation;
  $("animateParameter").disabled = state.reduced;
}
function syncControls() {
  for (const p of state.lesson.parameters) {
    const value = state.params[p.id];
    $("range-" + p.id).value = String(value);
    $("number-" + p.id).value = String(value);
    $("number-" + p.id).removeAttribute("aria-invalid");
  }
}
function schedule() {
  stopMotion();
  clearTimeout(state.debounce);
  state.revision++;
  state.controller?.abort();
  setBusy(true);
  error("");
  state.debounce = setTimeout(() => compute(), 150);
}
// Transport: loopback Python server when present, otherwise in-browser Pyodide (static hosting).
let staticMode = null;
async function apiFetch(url, options) {
  if (staticMode === null) {
    if (!["127.0.0.1", "localhost"].includes(location.hostname)) staticMode = true;
  }
  if (staticMode === null) {
    try {
      const probe = await fetch("/api/health", { cache: "no-store" });
      staticMode = !(probe.ok && (await probe.json()).name === "x3d.mathlab");
    } catch (_) {
      staticMode = true;
    }
  }
  if (staticMode && !document.body.dataset.transport) {
    document.body.dataset.transport = "pyodide";
    window.addEventListener("mathlab-static", (e) => {
      const n = $("stageMessage")?.querySelector("span");
      if (n && e.detail) n.textContent = e.detail;
    });
  }
  return staticMode ? window.MathLabStatic.fetch(url, options) : fetch(url, options);
}
async function compute() {
  clearTimeout(state.debounce);
  const revision = ++state.revision,
    lesson = state.lesson;
  state.controller?.abort();
  const controller = new AbortController();
  state.controller = controller;
  setBusy(true);
  try {
    const response = await apiFetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lesson: lesson.id, params: state.params }),
      signal: controller.signal,
    });
    let result;
    try {
      result = await response.json();
    } catch (_) {
      throw new Error("The local lab returned an unreadable response.");
    }
    if (revision !== state.revision) return false;
    if (!response.ok)
      throw new Error(
        typeof result.error === "string"
          ? result.error
          : result.error?.message ||
              result.message ||
              "These parameters could not be evaluated.",
      );
    if (!result.sample || typeof result.x3d !== "string")
      throw new Error("The local lab returned an incomplete model.");
    const shown = await showWorld(result, revision);
    if (!shown || revision !== state.revision) return false;
    state.accepted = result;
    state.params = { ...result.sample.params };
    syncControls();
    updateResult(result);
    error("");
    $("stageMessage").hidden = true;
    setBusy(false);
    return true;
  } catch (e) {
    if (e.name === "AbortError" || revision !== state.revision) return false;
    stopMotion();
    error(e.message);
    setBusy(true);
    $("updateLabel").hidden = true;
    if (!state.accepted) {
      $("stageMessage").hidden = false;
      $("stageMessage").querySelector("span").textContent =
        "The experiment needs a valid set of parameters.";
    }
    return false;
  }
}
function updateResult(result) {
  const { sample, identity } = result;
  $("formula").textContent = state.lesson.formula || sample.formula || "";
  const metrics = $("metrics");
  metrics.replaceChildren();
  for (const m of (sample.metrics || []).slice(0, 6)) {
    const card = node("div", "metric"),
      value = node("div", "metric-number", numeric(m.value));
    if (m.unit) value.append(node("small", "", m.unit));
    card.append(node("div", "metric-label", m.label || m.id), value);
    if (m.note) card.append(node("div", "metric-note", m.note));
    metrics.append(card);
  }
  const insights = $("insights");
  insights.replaceChildren();
  for (const text of sample.insights || [])
    insights.append(node("li", "", text));
  $("sourceText").value = result.x3d;
  const id =
    identity?.model_sha256 ||
    identity?.sample_sha256 ||
    identity?.card_sha256 ||
    identity?.sha256 ||
    sample.identity ||
    "";
  $("modelIdentity").textContent = id
    ? "MODEL " + String(id).slice(0, 16) + " · parameters retained" +
      (document.body.dataset.transport === "pyodide"
        ? " · IN-BROWSER PYTHON (PYODIDE " + window.MathLabStatic.pyodide + ")"
        : "")
    : "MODEL READY · parameters retained";
  const pointCount = (sample.primitives || []).reduce(
    (n, p) => n + (p.points?.length || 1),
    0,
  );
  $("sourceMeta").textContent =
    (sample.primitives?.length || 0) +
    " geometric parts · " +
    pointCount.toLocaleString() +
    " sampled points · " +
    new TextEncoder().encode(result.x3d).length.toLocaleString() +
    " X3D bytes";
  $("measurementScope").textContent =
    {
      linear: "Displayed transform · analytic determinant",
      derivative: "Finite differences · analytic reference",
      integral: "Sampled sum · analytic integral",
      fourier: "Finite series · whole-period error",
      lorenz: "RK4 · finite-time diagnostics",
      gradient: "Exact recurrence · sampled surface",
    }[sample.lesson] || "Current parameters · measured relationships";
}
async function nativeBrowser() {
  if (state.nativeFailed) return null;
  if (state.native) return state.native;
  if (state.nativeReady) return state.nativeReady;
  state.nativeReady = (async () => {
    try {
      const probe = document.createElement("canvas");
      if (!probe.getContext("webgl2") && !probe.getContext("webgl"))
        throw new Error("WebGL is unavailable");
      if (!window.X3D) throw new Error("The local X3D runtime did not load");
      await Promise.race([
        customElements.whenDefined("x3d-canvas"),
        new Promise((_, reject) =>
          setTimeout(
            () => reject(new Error("The X3D element did not initialize")),
            7000,
          ),
        ),
      ]);
      const browser = $("world").browser || window.X3D.getBrowser("#world");
      if (!browser || typeof browser.createX3DFromString !== "function")
        throw new Error("The X3D browser is unavailable");
      state.native = browser;
      return browser;
    } catch (_) {
      state.nativeFailed = true;
      return null;
    }
  })();
  return state.nativeReady;
}
function showWorld(result, revision) {
  state.worldQueue = state.worldQueue
    .catch(() => false)
    .then(() => replaceWorldInOrder(result, revision));
  return state.worldQueue;
}
async function replaceWorldInOrder(result, revision) {
  if (revision !== state.revision) return false;
  const browser = await nativeBrowser();
  if (revision !== state.revision) return false;
  if (browser && !state.projectionOnly) {
    try {
      const scene = await browser.createX3DFromString(result.x3d);
      if (revision !== state.revision) return false;
      await browser.replaceWorld(scene);
      if (revision !== state.revision) return false;
      // Zoom the authored viewpoint ~25% closer: the canvas now ends above the equation card,
      // so the generated framing (tuned for the taller box) left scenes small. View-only; the
      // X3D document, its bounds and its identity are untouched.
      try {
        const viewpoint = browser.activeViewpoint;
        if (viewpoint && viewpoint.fieldOfView > 0.2) viewpoint.fieldOfView *= 0.75;
      } catch (_) {}
      $("world").hidden = false;
      $("projection").hidden = true;
      $("rendererLabel").replaceChildren(
        node("i"),
        document.createTextNode("NATIVE X3D · X_ITE"),
      );
      $("viewHint").textContent = "Drag to orbit · scroll to look closer";
      $("projectionToggle").textContent = "2D";
      return true;
    } catch (e) {
      state.nativeFailed = true;
      state.native = null;
    }
  }
  if (revision !== state.revision) return false;
  drawProjection(result.sample);
  $("world").hidden = true;
  $("projection").hidden = false;
  $("rendererLabel").replaceChildren(
    node("i"),
    document.createTextNode(
      state.projectionOnly
        ? "2D PROJECTION · SAME MODEL"
        : "2D PROJECTION · NATIVE 3D UNAVAILABLE",
    ),
  );
  $("viewHint").textContent =
    "A two-dimensional projection of the same sampled geometry";
  $("projectionToggle").textContent = "3D";
  return true;
}
function drawProjection(sample) {
  const group = $("projectionGeometry");
  group.replaceChildren();
  const prims = sample.primitives || [],
    center = sample.bounds?.center || [0, 0, 0],
    threeD = ["lorenz", "gradient"].includes(sample.lesson);
  const project = (p) =>
    threeD
      ? [
          0.88 * (p[0] - center[0]) + 0.46 * (p[2] - center[2]),
          p[1] -
            center[1] -
            0.2 * (p[0] - center[0]) +
            0.28 * (p[2] - center[2]),
        ]
      : [p[0] - center[0], p[1] - center[1]];
  const positions = [];
  for (const p of prims) {
    if (Array.isArray(p.points))
      for (const v of p.points) positions.push(project(v));
    if (p.position) positions.push(project(p.position));
  }
  let extentX = Math.max(1, ...positions.map((p) => Math.abs(p[0]))),
    extentY = Math.max(1, ...positions.map((p) => Math.abs(p[1])));
  const scale = Math.min(820 / (extentX * 2), 450 / (extentY * 2)),
    xy = (p) => {
      const q = project(p);
      return [500 + q[0] * scale, 300 - q[1] * scale];
    };
  for (let i = 0; i <= 10; i++) {
    group.append(
      svg("line", {
        x1: 80 + i * 84,
        y1: 65,
        x2: 80 + i * 84,
        y2: 535,
        stroke: "#173246",
        "stroke-width": 0.7,
      }),
      svg("line", {
        x1: 80,
        y1: 65 + i * 47,
        x2: 920,
        y2: 65 + i * 47,
        stroke: "#173246",
        "stroke-width": 0.7,
      }),
    );
  }
  const color = (p) => {
    const c = Array.isArray(p.color) ? p.color : [0.4, 0.85, 0.82];
    return (
      "rgb(" +
      c.map((x) => Math.round(Math.max(0, Math.min(1, x)) * 255)).join(",") +
      ")"
    );
  };
  const surfaces = [];
  for (const p of prims) {
    if (p.kind === "mesh" && Array.isArray(p.indices)) {
      let face = [];
      const faces = [];
      for (const i of p.indices) {
        if (i === -1) {
          if (face.length >= 3) faces.push(face);
          face = [];
        } else if (p.points[i]) face.push(p.points[i]);
      }
      if (face.length >= 3) faces.push(face);
      for (const f of faces.slice(0, 2200)) {
        const depth = f.reduce((n, v) => n + v[2], 0) / f.length;
        surfaces.push({
          depth,
          shape: svg("polygon", {
            points: f.map((v) => xy(v).join(",")).join(" "),
            fill: color(p),
            "fill-opacity": 0.13,
            stroke: color(p),
            "stroke-opacity": 0.3,
            "stroke-width": 0.55,
          }),
        });
      }
    }
  }
  surfaces.sort((a, b) => a.depth - b.depth);
  for (const s of surfaces) group.append(s.shape);
  for (const p of prims) {
    const c = color(p);
    if (p.kind === "line" && p.points?.length) {
      group.append(
        svg("polyline", {
          points: p.points.map((v) => xy(v).join(",")).join(" "),
          fill: "none",
          stroke: c,
          "stroke-width": p.id?.includes("grid") ? 1 : 2.2,
          "stroke-opacity": p.id?.includes("grid") ? 0.4 : 0.95,
          "stroke-linejoin": "round",
          "stroke-linecap": "round",
        }),
      );
    } else if (p.kind === "sphere" && p.position) {
      const q = xy(p.position);
      group.append(
        svg("circle", {
          cx: q[0],
          cy: q[1],
          r: Math.max(2.2, Math.min(16, (p.radius || 0.08) * scale)),
          fill: c,
          stroke: "#fff6dd",
          "stroke-opacity": 0.5,
          "stroke-width": 1,
        }),
      );
    } else if (p.kind === "box" && p.position && p.size) {
      const q = xy(p.position);
      group.append(
        svg("rect", {
          x: q[0] - (p.size[0] * scale) / 2,
          y: q[1] - (p.size[1] * scale) / 2,
          width: Math.max(0.5, p.size[0] * scale),
          height: Math.max(0.5, p.size[1] * scale),
          fill: c,
          "fill-opacity": Math.max(0.08, 1 - (p.transparency ?? 0.65)),
          stroke: c,
          "stroke-opacity": 0.75,
          "stroke-width": 0.8,
        }),
      );
    }
  }
  $("projection").setAttribute(
    "aria-label",
    "Two-dimensional projection: " + sample.title,
  );
}
function buildStory() {
  const story = state.lesson.story || [];
  state.story = Math.max(0, Math.min(state.story, story.length - 1));
  const part = story[state.story] || {
    title: "Look first. Ask next.",
    text: state.lesson.description,
  };
  $("storyStep").textContent =
    String(state.story + 1).padStart(2, "0") +
    " / " +
    String(Math.max(1, story.length)).padStart(2, "0");
  $("storyTitle").textContent = part.title;
  $("storyText").textContent = part.text;
  $("storyCount").textContent =
    state.story + 1 + " of " + Math.max(1, story.length);
  $("storyPrev").disabled = state.story === 0;
  $("storyNext").disabled = state.story >= story.length - 1;
  const progress = $("storyProgress");
  progress.replaceChildren();
  story.forEach((_, i) =>
    progress.append(node("i", i <= state.story ? "active" : "")),
  );
}
function download(text, name, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = node("a");
  a.href = url;
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}
function exportX3D() {
  if (!state.accepted || $("downloadX3D").disabled) return;
  download(
    state.accepted.x3d,
    "mathlab-" + state.lesson.id + ".x3d",
    "model/x3d+xml",
  );
  message("X3D world saved with its lesson parameters.");
}
async function play() {
  if (state.playing) {
    stopMotion();
    return;
  }
  if (state.reduced || !state.lesson.animation) return;
  state.playing = true;
  const token = ++state.playToken;
  $("animateParameter").textContent = "Ⅱ Pause the motion";
  $("animateParameter").setAttribute("aria-pressed", "true");
  const animation = state.lesson.animation;
  let direction = state.params[animation.parameter] >= animation.max ? -1 : 1,
    previous = performance.now();
  while (state.playing && token === state.playToken && !document.hidden) {
    const now = performance.now(),
      dt = Math.min(0.4, (now - previous) / 1000);
    previous = now;
    const range = animation.max - animation.min;
    let value =
      state.params[animation.parameter] +
      dt * (animation.speed || 0.6) * direction;
    if (animation.mode === "pingpong") {
      if (value >= animation.max) {
        value = animation.max;
        direction = -1;
      }
      if (value <= animation.min) {
        value = animation.min;
        direction = 1;
      }
    } else if (value > animation.max)
      value = animation.min + ((value - animation.min) % range);
    state.params[animation.parameter] = Number(value.toFixed(5));
    syncControls();
    const ok = await compute();
    if (!ok) break;
    await new Promise((resolve) => setTimeout(resolve, 170));
  }
  if (token === state.playToken) stopMotion();
}
for (const b of document.querySelectorAll("[data-panel]")) {
  b.onclick = () => changePanel(b.dataset.panel);
  b.onkeydown = (e) => {
    const tabs = [...document.querySelectorAll("[data-panel]")],
      i = tabs.indexOf(b);
    let next;
    if (e.key === "ArrowRight") next = (i + 1) % tabs.length;
    else if (e.key === "ArrowLeft") next = (i + tabs.length - 1) % tabs.length;
    else if (e.key === "Home") next = 0;
    else if (e.key === "End") next = tabs.length - 1;
    else return;
    e.preventDefault();
    changePanel(tabs[next].dataset.panel);
    tabs[next].focus();
  };
}
$("resetParameters").onclick = () => {
  stopMotion();
  state.params = defaults(state.lesson);
  syncControls();
  resetPrediction();
  compute();
};
$("revealAnswer").onclick = () => {
  const shown = !$("challengeAnswer").hidden;
  $("challengeAnswer").hidden = shown;
  $("revealAnswer").textContent = shown
    ? "Reveal the reasoning ↘"
    : "Hide the reasoning ↑";
};
$("storyPrev").onclick = () => {
  state.story--;
  buildStory();
};
$("storyNext").onclick = () => {
  state.story++;
  buildStory();
};
$("backToControls").onclick = () => changePanel("explore");
$("downloadX3D").onclick = exportX3D;
$("sourceDownload").onclick = exportX3D;
$("saveCard").onclick = () => {
  if (!state.accepted || $("saveCard").disabled) return;
  const card = {
    schema: "x3d.mathlab.lesson-card/1",
    lesson: state.lesson.id,
    params: state.accepted.sample.params,
    prediction: $("predictionText").value.slice(0, 2000),
  };
  download(
    JSON.stringify(card, null, 2) + "\n",
    "mathlab-" + state.lesson.id + ".json",
    "application/json",
  );
  message("Lesson card saved. Reopen it to continue exploring.");
};
$("importButton").onclick = () => $("cardFile").click();
$("cardFile").onchange = async (e) => {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;
  try {
    if (file.size > 32768)
      throw new Error("Lesson cards must be smaller than 32 KiB.");
    const card = JSON.parse(await file.text());
    if (
      card.schema !== "x3d.mathlab.lesson-card/1" ||
      typeof card.lesson !== "string" ||
      !card.params ||
      typeof card.params !== "object" ||
      Array.isArray(card.params)
    )
      throw new Error("That file is not a Math Lab lesson card.");
    const lesson = state.lessons.find((l) => l.id === card.lesson);
    if (!lesson) throw new Error("That lesson is not available.");
    const keys = new Set(lesson.parameters.map((p) => p.id));
    if (Object.keys(card.params).some((k) => !keys.has(k)))
      throw new Error("The card contains an unknown parameter.");
    for (const p of lesson.parameters) {
      if (!(p.id in card.params)) continue;
      const v = card.params[p.id];
      if (
        !finite(v) ||
        v < p.min ||
        v > p.max ||
        (p.type === "integer" && !Number.isInteger(v))
      )
        throw new Error("The card has an invalid " + p.label + ".");
    }
    choose(card.lesson, { ...defaults(lesson), ...card.params });
    $("predictionText").value =
      typeof card.prediction === "string" ? card.prediction.slice(0, 2000) : "";
    message("Lesson card opened; the model is being recomputed.");
  } catch (e) {
    message(e.message);
  }
};
$("copySource").onclick = async () => {
  if (!state.accepted || $("copySource").disabled) return;
  try {
    await navigator.clipboard.writeText(state.accepted.x3d);
    message("Current X3D source copied.");
  } catch (_) {
    $("sourceText").focus();
    $("sourceText").select();
    message("Source selected. Press Ctrl+C or Command+C to copy.");
  }
};
$("cameraReset").onclick = async () => {
  if (!state.accepted || $("cameraReset").disabled) return;
  try {
    if (state.native && !state.projectionOnly && !state.nativeFailed)
      state.native.changeViewpoint("MathLabView");
    else drawProjection(state.accepted.sample);
  } catch (_) {
    await showWorld(state.accepted, state.revision);
  }
  message("Back to the authored view.");
};
$("projectionToggle").onclick = async () => {
  if (!state.accepted || $("projectionToggle").disabled) return;
  state.projectionOnly = !state.projectionOnly;
  await showWorld(state.accepted, state.revision);
};
$("fullscreen").onclick = async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await $("stage").requestFullscreen();
  } catch (_) {
    message("Fullscreen is unavailable in this browser.");
  }
};
$("downloadManim").onclick = async () => {
  if (!state.accepted || $("downloadManim").disabled) return;
  const revision = state.revision,
    lesson = state.lesson.id,
    params = { ...state.accepted.sample.params };
  $("downloadManim").disabled = true;
  try {
    const response = await apiFetch("/api/manim", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lesson, params }),
    });
    const result = await response.json();
    if (revision !== state.revision) return;
    if (!response.ok || typeof result.source !== "string")
      throw new Error(
        typeof result.error === "string"
          ? result.error
          : result.message || "The Manim source could not be generated.",
      );
    download(result.source, "mathlab-" + lesson + ".py", "text/x-python");
    message("Manim source saved. Review it before rendering locally.");
  } catch (e) {
    if (revision === state.revision) message(e.message);
  } finally {
    if (revision === state.revision) $("downloadManim").disabled = false;
  }
};
$("animateParameter").onclick = play;
const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
function comfort() {
  state.reduced = $("reduceMotion").checked || motionQuery.matches;
  document.body.classList.toggle("calm", state.reduced);
  $("animateParameter").disabled = state.reduced;
  if (state.reduced) stopMotion();
}
$("reduceMotion").onchange = comfort;
motionQuery.addEventListener?.("change", comfort);
comfort();
document.addEventListener("visibilitychange", () => {
  if (document.hidden) stopMotion();
});
$("guideButton").onclick = () =>
  window.open((location.pathname.includes("/web/") ? "../docs/" : "/docs/") + "Mathlab-Field-Guide.html", "_blank", "noopener");
async function initialize() {
  try {
    const response = await apiFetch("/api/catalog");
    if (!response.ok)
      throw new Error("The local Math Lab service is not responding.");
    const data = await response.json();
    if (!Array.isArray(data.lessons) || !data.lessons.length)
      throw new Error("The lesson collection is empty.");
    state.lessons = data.lessons;
    buildNav();
    const requested = location.hash.slice(1);
    choose(
      state.lessons.some((l) => l.id === requested)
        ? requested
        : state.lessons[0].id,
    );
  } catch (e) {
    $("stageMessage").querySelector("span").textContent =
      "The lab could not start.";
    error(e.message);
    $("rendererLabel").textContent = "LOCAL SERVICE UNAVAILABLE";
  }
}
initialize();

// Keep the 3D view clear of the equation card: size the canvas to the space above it.
(() => {
  const card = document.querySelector(".equation-card"),
    stage = $("stage");
  if (!card || !stage || typeof ResizeObserver !== "function") return;
  new ResizeObserver(() =>
    stage.style.setProperty("--eq-h", Math.ceil(card.offsetHeight + 24) + "px"),
  ).observe(card);
})();
