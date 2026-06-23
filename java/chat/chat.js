const socket = io();
const room = document.body.dataset.room;
const role = document.body.dataset.role;

const chatBox = document.getElementById("chat-box");
const msgInput = document.getElementById("msg-input");
const sendBtn = document.getElementById("send-btn");
const attachBtn = document.getElementById("attach-btn");
const stickersBtn = document.getElementById("stickers-btn");
const stickerPanel = document.getElementById("sticker-panel");
const fileInput = document.getElementById("file-input");
const pendingFilesEl = document.getElementById("pending-files");

let pendingFiles = [];

function closeStickerPanel() {
  stickerPanel.hidden = true;
  stickerPanel.setAttribute("aria-hidden", "true");
}

function openStickerPanel() {
  stickerPanel.hidden = false;
  stickerPanel.setAttribute("aria-hidden", "false");
}

socket.emit("join", { room });

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function renderPendingFiles() {
  if (!pendingFiles.length) {
    pendingFilesEl.hidden = true;
    pendingFilesEl.innerHTML = "";
    return;
  }

  pendingFilesEl.hidden = false;
  pendingFilesEl.innerHTML = pendingFiles
    .map(
      (file, index) => `
        <div class="pending-file">
          <div class="pending-file-meta">
            <strong>${escapeHtml(file.name)}</strong>
            <span>${escapeHtml(formatSize(file.size))}</span>
          </div>
          <button type="button" class="remove-file-btn" data-index="${index}">×</button>
        </div>
      `
    )
    .join("");

  pendingFilesEl.querySelectorAll(".remove-file-btn").forEach((button) => {
    button.addEventListener("click", () => {
      pendingFiles.splice(Number(button.dataset.index), 1);
      renderPendingFiles();
    });
  });
}

function renderMessage(data) {
  const div = document.createElement("div");
  div.className = `message ${data.sender}`;

  const textHtml = data.text ? `<p>${escapeHtml(data.text)}</p>` : "";
  const stickerHtml = data.sticker
    ? `<div class="message-sticker"><img src="${data.sticker}" alt="Стікер" /></div>`
    : "";

  const filesHtml = (data.files || [])
    .map((file) => {
      const preview = file.is_image
        ? `<a class="file-preview-link" href="${file.url}" target="_blank" rel="noopener">
             <img class="file-preview-image" src="${file.url}" alt="${escapeHtml(file.name)}" />
           </a>`
        : "";

      return `
        <a class="file-card" href="${file.url}" target="_blank" rel="noopener">
          <div class="file-card-top">
            <img class="file-card-icon" src="/static/resources/resources-assets/Icon line messenger pic - Made in yan.ua.svg" alt="" />
            <div class="file-card-meta">
              <strong>${escapeHtml(file.name)}</strong>
              <span>${escapeHtml(formatSize(file.size))}</span>
            </div>
          </div>
          ${preview}
        </a>
      `;
    })
    .join("");

  const timeStr = data.time || new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  div.innerHTML = `
    <div class="message-body">
      ${stickerHtml}
      ${textHtml}
      ${filesHtml}
    </div>
    <small class="timestamp">${timeStr}</small>
  `;

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function uploadSelectedFiles(files) {
  const formData = new FormData();
  formData.append("room", room);
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || "upload_failed");
  }

  pendingFiles = pendingFiles.concat(payload.files || []);
  renderPendingFiles();
}

function sendMessage({ sticker = "" } = {}) {
  const text = msgInput.value.trim();
  if (!text && !pendingFiles.length && !sticker) {
    return;
  }

  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  socket.emit("send_message", {
    room,
    text,
    role,
    time: now,
    files: pendingFiles,
    sticker,
  });

  msgInput.value = "";
  pendingFiles = [];
  renderPendingFiles();
  closeStickerPanel();
}

socket.on("history", (items) => {
  chatBox.innerHTML = "";
  items.forEach(renderMessage);
});

socket.on("receive_message", (data) => {
  renderMessage(data);
});

sendBtn.addEventListener("click", () => sendMessage());

msgInput.addEventListener("keypress", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

attachBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", async () => {
  const files = Array.from(fileInput.files || []);
  if (!files.length) return;

  attachBtn.disabled = true;
  try {
    await uploadSelectedFiles(files);
  } catch (error) {
    alert("Не вдалося завантажити файл");
  } finally {
    attachBtn.disabled = false;
    fileInput.value = "";
  }
});

stickersBtn.addEventListener("click", () => {
  if (stickerPanel.hidden) {
    openStickerPanel();
  } else {
    closeStickerPanel();
  }
});

document.querySelectorAll(".sticker-btn").forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage({ sticker: button.dataset.stickerUrl });
  });
});

document.addEventListener("click", (event) => {
  const clickedInsidePanel = stickerPanel.contains(event.target);
  const clickedToggle = stickersBtn.contains(event.target);
  if (!clickedInsidePanel && !clickedToggle) {
    closeStickerPanel();
  }
});
