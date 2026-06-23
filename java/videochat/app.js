const roomInput = document.getElementById("roomKey");
const joinBtn = document.getElementById("joinBtn");
const leaveBtn = document.getElementById("leaveBtn");
const startLessonBtn = document.getElementById("startLessonBtn");
const toggleMicBtn = document.getElementById("toggleMicBtn");
const toggleCameraBtn = document.getElementById("toggleCameraBtn");
const statusEl = document.getElementById("status");
const permissionNotice = document.getElementById("permissionNotice");
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const lessonBoard = document.getElementById("lessonBoard");
const boardCanvas = document.getElementById("boardCanvas");
const previewCanvas = document.getElementById("previewCanvas");
const drawingTools = document.getElementById("drawingTools");
const boardTools = document.getElementById("boardTools");
const boardMenuBtn = document.getElementById("boardMenuBtn");
const boardMenu = document.getElementById("boardMenu");
const shapeMenuBtn = document.getElementById("shapeMenuBtn");
const shapeMenu = document.getElementById("shapeMenu");
const endLessonBtn = document.getElementById("endLessonBtn");
const boardCtx = boardCanvas.getContext("2d");
const previewCtx = previewCanvas.getContext("2d");

let ws = null;
let pc = null;
let localStream = null;
let room = "";
let micEnabled = true;
let cameraEnabled = true;
let lessonActive = false;
let boardBackground = "blank";
let currentTool = "pencil";
let currentShape = "rectangle";
let isDrawing = false;
let lastPoint = null;
let shapeStart = null;
let boardActions = [];

function setStatus(text) {
  statusEl.textContent = text;
}

function showNotice(text) {
  permissionNotice.textContent = text;
  permissionNotice.hidden = false;
}

function hideNotice() {
  permissionNotice.textContent = "";
  permissionNotice.hidden = true;
}

function isLocalhost() {
  return ["localhost", "127.0.0.1", "::1"].includes(location.hostname);
}

function mediaApiAvailable() {
  return Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

function updateDeviceButtons() {
  const hasStream = Boolean(localStream);
  toggleMicBtn.disabled = !hasStream;
  toggleCameraBtn.disabled = !hasStream;
  startLessonBtn.disabled = !ws;
  toggleMicBtn.textContent = `Мікрофон: ${micEnabled ? "увімкнено" : "вимкнено"}`;
  toggleCameraBtn.textContent = `Камера: ${cameraEnabled ? "увімкнена" : "вимкнена"}`;
  toggleMicBtn.classList.toggle("is-off", hasStream && !micEnabled);
  toggleCameraBtn.classList.toggle("is-off", hasStream && !cameraEnabled);
}

function sendSignal(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(message);
  }
}

function resizeBoardCanvas() {
  const ratio = window.devicePixelRatio || 1;
  const rect = lessonBoard.getBoundingClientRect();
  const cssWidth = Math.max(1, rect.width);
  const cssHeight = Math.max(1, rect.height);
  const width = Math.max(1, Math.floor(cssWidth * ratio));
  const height = Math.max(1, Math.floor(cssHeight * ratio));
  if (
    boardCanvas.width === width &&
    boardCanvas.height === height &&
    previewCanvas.width === width &&
    previewCanvas.height === height
  ) {
    return;
  }

  boardCanvas.width = width;
  boardCanvas.height = height;
  boardCtx.setTransform(ratio, 0, 0, ratio, 0, 0);
  previewCanvas.width = width;
  previewCanvas.height = height;
  previewCtx.setTransform(ratio, 0, 0, ratio, 0, 0);
  redrawBoard();
}

function clearPreview() {
  const rect = lessonBoard.getBoundingClientRect();
  previewCtx.clearRect(0, 0, rect.width, rect.height);
}

function pointFromEvent(event) {
  const rect = boardCanvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left) / rect.width,
    y: (event.clientY - rect.top) / rect.height,
  };
}

function denormalize(point) {
  const rect = lessonBoard.getBoundingClientRect();
  return {
    x: point.x * rect.width,
    y: point.y * rect.height,
  };
}

function drawLine(from, to, mode = "pencil") {
  const start = denormalize(from);
  const end = denormalize(to);
  boardCtx.save();
  boardCtx.lineCap = "round";
  boardCtx.lineJoin = "round";
  boardCtx.lineWidth = mode === "eraser" ? 24 : 3;
  boardCtx.globalCompositeOperation = mode === "eraser" ? "destination-out" : "source-over";
  boardCtx.strokeStyle = "#111815";
  boardCtx.beginPath();
  boardCtx.moveTo(start.x, start.y);
  boardCtx.lineTo(end.x, end.y);
  boardCtx.stroke();
  boardCtx.restore();
}

function drawStraightLine(startPoint, endPoint, ctx = boardCtx, preview = false) {
  const start = denormalize(startPoint);
  const end = denormalize(endPoint);
  ctx.save();
  ctx.lineWidth = preview ? 2 : 3;
  ctx.setLineDash(preview ? [8, 7] : []);
  ctx.strokeStyle = preview ? "rgba(17, 24, 21, 0.55)" : "#111815";
  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(end.x, end.y);
  ctx.stroke();
  ctx.restore();
}

function drawCompassCircle(startPoint, endPoint, ctx = boardCtx, preview = false) {
  const start = denormalize(startPoint);
  const end = denormalize(endPoint);
  const radius = Math.hypot(end.x - start.x, end.y - start.y);
  ctx.save();
  ctx.lineWidth = preview ? 2 : 3;
  ctx.setLineDash(preview ? [8, 7] : []);
  ctx.strokeStyle = preview ? "rgba(17, 24, 21, 0.55)" : "#111815";
  ctx.beginPath();
  ctx.arc(start.x, start.y, radius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

function drawProtractorAngle(startPoint, endPoint, ctx = boardCtx, preview = false) {
  const start = denormalize(startPoint);
  const end = denormalize(endPoint);
  const angle = Math.atan2(end.y - start.y, end.x - start.x);
  const radius = Math.min(90, Math.max(36, Math.hypot(end.x - start.x, end.y - start.y) * 0.45));
  ctx.save();
  ctx.lineWidth = preview ? 2 : 3;
  ctx.setLineDash(preview ? [8, 7] : []);
  ctx.strokeStyle = preview ? "rgba(17, 24, 21, 0.55)" : "#111815";
  ctx.beginPath();
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(start.x + radius * 1.35, start.y);
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(end.x, end.y);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(start.x, start.y, radius, Math.min(0, angle), Math.max(0, angle));
  ctx.stroke();
  ctx.restore();
}

function drawShape(startPoint, endPoint, shape = currentShape, ctx = boardCtx, preview = false) {
  const start = denormalize(startPoint);
  const end = denormalize(endPoint);
  const left = Math.min(start.x, end.x);
  const top = Math.min(start.y, end.y);
  const width = Math.abs(end.x - start.x);
  const height = Math.abs(end.y - start.y);
  ctx.save();
  ctx.lineWidth = preview ? 2 : 3;
  ctx.setLineDash(preview ? [8, 7] : []);
  ctx.strokeStyle = preview ? "rgba(17, 24, 21, 0.55)" : "#111815";
  ctx.beginPath();
  if (shape === "circle") {
    ctx.ellipse(left + width / 2, top + height / 2, width / 2, height / 2, 0, 0, Math.PI * 2);
  } else if (shape === "triangle") {
    ctx.moveTo(left + width / 2, top);
    ctx.lineTo(left + width, top + height);
    ctx.lineTo(left, top + height);
    ctx.closePath();
  } else {
    ctx.rect(left, top, width, height);
  }
  ctx.stroke();
  ctx.restore();
}

function drawShapePreview(startPoint, endPoint) {
  clearPreview();
  if (currentTool === "compass") {
    drawCompassCircle(startPoint, endPoint, previewCtx, true);
  } else if (currentTool === "protractor") {
    drawProtractorAngle(startPoint, endPoint, previewCtx, true);
  } else if (currentTool === "line") {
    drawStraightLine(startPoint, endPoint, previewCtx, true);
  } else if (currentTool === "shape") {
    drawShape(startPoint, endPoint, currentShape, previewCtx, true);
  }
}

function drawBoardAction(action) {
  if (action.tool === "pencil" || action.tool === "eraser") {
    drawLine(action.from, action.to, action.tool);
  } else if (action.tool === "compass") {
    drawCompassCircle(action.from, action.to);
  } else if (action.tool === "protractor") {
    drawProtractorAngle(action.from, action.to);
  } else if (action.tool === "line") {
    drawStraightLine(action.from, action.to);
  } else if (action.tool === "shape") {
    drawShape(action.from, action.to, action.shape || "rectangle");
  }
}

function redrawBoard() {
  const rect = lessonBoard.getBoundingClientRect();
  boardCtx.clearRect(0, 0, rect.width, rect.height);
  for (const action of boardActions) {
    drawBoardAction(action);
  }
}

function applyBoardAction(action, shouldBroadcast = true) {
  boardActions.push(action);
  drawBoardAction(action);

  if (shouldBroadcast) {
    sendSignal({ type: "board-action", action });
  }
}

function setDrawingTool(tool) {
  currentTool = tool;
  document.querySelectorAll(".drawing-tool").forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.tool === currentTool);
  });
}

function setBoardBackground(name, shouldBroadcast = true) {
  const allowed = new Set(["blank", "grid", "lines", "dots", "graph"]);
  boardBackground = allowed.has(name) ? name : "blank";
  lessonBoard.className = `lesson-board board-${boardBackground}`;
  boardMenu.hidden = true;
  if (shouldBroadcast) {
    sendSignal({ type: "board-background", background: boardBackground });
  }
}

function setLessonMode(active, shouldBroadcast = true) {
  lessonActive = active;
  document.body.classList.toggle("lesson-active", lessonActive);
  lessonBoard.hidden = !lessonActive;
  drawingTools.hidden = !lessonActive;
  boardTools.hidden = !lessonActive;
  startLessonBtn.classList.toggle("is-active", lessonActive);
  startLessonBtn.textContent = lessonActive ? "Урок триває" : "Розпочати урок";
  boardMenu.hidden = true;
  shapeMenu.hidden = true;
  if (lessonActive) {
    resizeBoardCanvas();
    setBoardBackground(boardBackground, false);
    setStatus("Режим уроку активний");
  } else {
    setStatus("Режим уроку завершено");
  }
  if (shouldBroadcast) {
    sendSignal({ type: lessonActive ? "lesson-start" : "lesson-end" });
    if (lessonActive) {
      sendSignal({ type: "board-background", background: boardBackground });
    }
  }
}

function createSignalSocket(roomKey) {
  const socket = io("/videochat", { query: { room: roomKey } });
  const signal = {
    readyState: WebSocket.CONNECTING,
    onopen: null,
    onmessage: null,
    onclose: null,
    onerror: null,
    send(message) {
      socket.emit("signal", message);
    },
    close() {
      socket.disconnect();
    },
  };

  socket.on("connect", () => {
    signal.readyState = WebSocket.OPEN;
    if (signal.onopen) signal.onopen();
  });

  socket.on("signal", (message) => {
    if (signal.onmessage) signal.onmessage({ data: JSON.stringify(message) });
  });

  socket.on("disconnect", (reason) => {
    signal.readyState = WebSocket.CLOSED;
    if (signal.onclose) signal.onclose({ code: 1000, reason });
  });

  socket.on("connect_error", (error) => {
    signal.readyState = WebSocket.CLOSED;
    if (signal.onerror) signal.onerror(error);
    if (signal.onclose) signal.onclose({ code: 1006, reason: error.message });
  });

  return signal;
}

async function startLocal() {
  if (localStream) return localStream;
  hideNotice();

  if (!window.isSecureContext && !isLocalhost()) {
    throw new Error("insecure-context");
  }

  if (!mediaApiAvailable()) {
    throw new Error("media-api-unavailable");
  }

  localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  micEnabled = true;
  cameraEnabled = true;
  localVideo.srcObject = localStream;
  updateDeviceButtons();
  return localStream;
}

function createPeer() {
  if (pc) return pc;
  pc = new RTCPeerConnection({
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
  });

  pc.onicecandidate = (event) => {
    if (event.candidate && ws) {
      ws.send({ type: "ice", candidate: event.candidate });
    }
  };

  pc.ontrack = (event) => {
    const [stream] = event.streams;
    if (stream) {
      remoteVideo.srcObject = stream;
    }
  };

  pc.onconnectionstatechange = () => {
    if (!pc) return;
    setStatus(`Стан з'єднання: ${pc.connectionState}`);
  };

  if (localStream) {
    for (const track of localStream.getTracks()) {
      pc.addTrack(track, localStream);
    }
  }

  return pc;
}

async function handleOffer(sdp) {
  const peer = createPeer();
  await peer.setRemoteDescription(sdp);
  const answer = await peer.createAnswer();
  await peer.setLocalDescription(answer);
  ws.send({ type: "answer", sdp: peer.localDescription });
  setStatus("Надіслано відповідь на підключення");
}

async function handleAnswer(sdp) {
  if (!pc) return;
  await pc.setRemoteDescription(sdp);
  setStatus("Отримано відповідь, з'єднуємось…");
}

async function handleIce(candidate) {
  if (!pc) return;
  try {
    await pc.addIceCandidate(candidate);
  } catch (err) {
    console.warn("ICE error", err);
  }
}

function resetPeer() {
  if (pc) {
    pc.ontrack = null;
    pc.onicecandidate = null;
    pc.close();
    pc = null;
  }
  remoteVideo.srcObject = null;
}

function stopLocal() {
  if (!localStream) return;
  for (const track of localStream.getTracks()) {
    track.stop();
  }
  localStream = null;
  localVideo.srcObject = null;
  micEnabled = true;
  cameraEnabled = true;
  updateDeviceButtons();
}

function toggleTrack(kind) {
  if (!localStream) return;
  const tracks = kind === "audio" ? localStream.getAudioTracks() : localStream.getVideoTracks();
  if (!tracks.length) return;

  const enabled = !tracks[0].enabled;
  for (const track of tracks) {
    track.enabled = enabled;
  }

  if (kind === "audio") {
    micEnabled = enabled;
    setStatus(enabled ? "Мікрофон увімкнено" : "Мікрофон вимкнено");
  } else {
    cameraEnabled = enabled;
    setStatus(enabled ? "Камеру увімкнено" : "Камеру вимкнено");
  }

  updateDeviceButtons();
}

async function joinRoom() {
  room = roomInput.value.trim();
  if (!room) {
    setStatus("Вкажи ключ кімнати");
    return;
  }

  joinBtn.disabled = true;
  leaveBtn.disabled = false;
  roomInput.disabled = true;
  setStatus("Підключення до кімнати…");

  try {
    await startLocal();
  } catch (err) {
    console.warn("Media access error", err);
    let message = "Немає доступу до камери/мікрофона. Натисни на значок замка біля адреси сайту й дозволь камеру та мікрофон, потім онови сторінку.";

    if (err && err.message === "insecure-context") {
      message = "Браузер блокує камеру й мікрофон на HTTP-адресі в локальній мережі. Відкрий відеочат через HTTPS або через localhost на цьому комп'ютері.";
    } else if (err && err.message === "media-api-unavailable") {
      message = "Цей браузер або режим сторінки не дає доступу до камери й мікрофона. Спробуй Chrome/Edge/Firefox і відкрий сторінку через HTTPS.";
    } else if (err && err.name === "NotFoundError") {
      message = "Камеру або мікрофон не знайдено. Перевір, чи пристрій підключений і не зайнятий іншою програмою.";
    } else if (err && (err.name === "NotAllowedError" || err.name === "SecurityError")) {
      message = "Доступ до камери або мікрофона заборонено. Дозволь доступ у браузері для цієї сторінки й натисни «Підключитись» ще раз.";
    } else if (err && err.name === "NotReadableError") {
      message = "Камера або мікрофон зайняті іншою програмою. Закрий інші дзвінки/додатки й спробуй знову.";
    }

    setStatus("Камера/мікрофон недоступні");
    showNotice(message);
    joinBtn.disabled = false;
    leaveBtn.disabled = true;
    roomInput.disabled = false;
    return;
  }

  ws = createSignalSocket(room);

  ws.onopen = () => {
    setStatus("Сигнальний канал відкрито");
    updateDeviceButtons();
  };

  ws.onmessage = async (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      return;
    }

    if (msg.type === "role") {
      if (msg.role === "offerer") {
        const peer = createPeer();
        const offer = await peer.createOffer();
        await peer.setLocalDescription(offer);
        ws.send({ type: "offer", sdp: peer.localDescription });
        setStatus("Надіслано запит на підключення");
      } else {
        setStatus("Очікуємо іншого учасника…");
      }
      return;
    }

    if (msg.type === "peer-joined") {
      setStatus("Другий учасник приєднався");
      if (lessonActive) {
        sendSignal({ type: "lesson-start" });
        sendSignal({ type: "board-background", background: boardBackground });
      }
      return;
    }

    if (msg.type === "offer") {
      await handleOffer(msg.sdp);
      return;
    }

    if (msg.type === "answer") {
      await handleAnswer(msg.sdp);
      return;
    }

    if (msg.type === "ice") {
      await handleIce(msg.candidate);
      return;
    }

    if (msg.type === "peer-left") {
      resetPeer();
      setStatus("Співрозмовник вийшов. Очікуємо нового…");
      return;
    }

    if (msg.type === "lesson-start") {
      setLessonMode(true, false);
      return;
    }

    if (msg.type === "lesson-end") {
      setLessonMode(false, false);
      return;
    }

    if (msg.type === "board-background") {
      setBoardBackground(msg.background, false);
      return;
    }

    if (msg.type === "board-action") {
      applyBoardAction(msg.action, false);
      return;
    }
  };

  ws.onclose = (event) => {
    if (event.code === 4002) {
      setStatus("Кімната вже зайнята (максимум 2 учасники)");
    } else if (event.code === 4001) {
      setStatus("Невірний ключ кімнати");
    } else {
      setStatus("З'єднання завершене");
    }
    cleanup();
  };

  ws.onerror = () => {
    setStatus("Помилка підключення до сервера");
  };
}

function cleanup() {
  if (ws) {
    ws.onopen = null;
    ws.onmessage = null;
    ws.onclose = null;
    ws.onerror = null;
    ws.close();
    ws = null;
  }
  resetPeer();
  stopLocal();
  setLessonMode(false, false);
  joinBtn.disabled = false;
  leaveBtn.disabled = true;
  roomInput.disabled = false;
  startLessonBtn.disabled = true;
  updateDeviceButtons();
}

joinBtn.addEventListener("click", () => {
  if (!ws) joinRoom();
});

leaveBtn.addEventListener("click", () => {
  setStatus("Ви вийшли з кімнати");
  cleanup();
});

startLessonBtn.addEventListener("click", () => {
  if (startLessonBtn.disabled) return;
  setLessonMode(true);
});

endLessonBtn.addEventListener("click", () => {
  setLessonMode(false);
});

boardMenuBtn.addEventListener("click", () => {
  boardMenu.hidden = !boardMenu.hidden;
  shapeMenu.hidden = true;
});

boardMenu.addEventListener("click", (event) => {
  const button = event.target.closest("[data-board-bg]");
  if (!button) return;
  setBoardBackground(button.dataset.boardBg);
});

drawingTools.addEventListener("click", (event) => {
  const button = event.target.closest("[data-tool]");
  if (!button) return;
  setDrawingTool(button.dataset.tool);
  if (button.dataset.tool !== "shape") {
    shapeMenu.hidden = true;
  }
});

shapeMenuBtn.addEventListener("click", () => {
  shapeMenu.hidden = !shapeMenu.hidden;
  boardMenu.hidden = true;
});

shapeMenu.addEventListener("click", (event) => {
  const button = event.target.closest("[data-shape]");
  if (!button) return;
  currentShape = button.dataset.shape;
  setDrawingTool("shape");
  shapeMenu.hidden = true;
});

boardCanvas.addEventListener("pointerdown", (event) => {
  if (!lessonActive) return;
  event.preventDefault();
  boardCanvas.setPointerCapture(event.pointerId);
  isDrawing = true;
  lastPoint = pointFromEvent(event);
  shapeStart = lastPoint;
});

boardCanvas.addEventListener("pointermove", (event) => {
  if (!isDrawing || !lastPoint) return;
  event.preventDefault();
  const nextPoint = pointFromEvent(event);
  if (currentTool === "pencil" || currentTool === "eraser") {
    applyBoardAction({ tool: currentTool, from: lastPoint, to: nextPoint });
    lastPoint = nextPoint;
  } else if (["compass", "protractor", "line", "shape"].includes(currentTool)) {
    drawShapePreview(shapeStart, nextPoint);
  }
});

boardCanvas.addEventListener("pointerup", (event) => {
  if (!isDrawing || !shapeStart) return;
  event.preventDefault();
  const endPoint = pointFromEvent(event);
  clearPreview();
  if (["compass", "protractor", "line", "shape"].includes(currentTool)) {
    applyBoardAction({ tool: currentTool, shape: currentShape, from: shapeStart, to: endPoint });
  }
  isDrawing = false;
  lastPoint = null;
  shapeStart = null;
});

boardCanvas.addEventListener("pointercancel", () => {
  clearPreview();
  isDrawing = false;
  lastPoint = null;
  shapeStart = null;
});

document.addEventListener("click", (event) => {
  if (!boardMenu.hidden && !boardMenuBtn.contains(event.target) && !boardMenu.contains(event.target)) {
    boardMenu.hidden = true;
  }
  if (!shapeMenu.hidden && !shapeMenuBtn.contains(event.target) && !shapeMenu.contains(event.target)) {
    shapeMenu.hidden = true;
  }
});

window.addEventListener("resize", () => {
  if (lessonActive) resizeBoardCanvas();
});

toggleMicBtn.addEventListener("click", () => {
  toggleTrack("audio");
});

toggleCameraBtn.addEventListener("click", () => {
  toggleTrack("video");
});

const params = new URLSearchParams(location.search);
const preset = params.get("room");
if (preset) {
  roomInput.value = preset;
}

updateDeviceButtons();
setDrawingTool(currentTool);
