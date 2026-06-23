const state = {
  teachers: [],
  bookings: [],
  selectedTeacher: null,
  selectedDate: null,
  selectedTime: null,
  duration: 60,
};

const teachersEl = document.getElementById("teachers");
const slotsEl = document.getElementById("slots");
const statusText = document.getElementById("statusText");
const dateInput = document.getElementById("dateInput");
const durationSelect = document.getElementById("durationSelect");
const bookBtn = document.getElementById("bookBtn");
const resultEl = document.getElementById("result");

const SLOT_STEP = 30; // minutes
const START_HOUR = 8;
const END_HOUR = 20; // last slot starts at 19:30

function toMinutes(time) {
  const [h, m] = time.split(":").map(Number);
  return h * 60 + m;
}

function minutesToTime(mins) {
  const h = Math.floor(mins / 60).toString().padStart(2, "0");
  const m = (mins % 60).toString().padStart(2, "0");
  return `${h}:${m}`;
}

function buildSlots() {
  const slots = [];
  for (let m = START_HOUR * 60; m < END_HOUR * 60; m += SLOT_STEP) {
    slots.push(minutesToTime(m));
  }
  return slots;
}

function bookingOverlaps(booking, startMin, endMin) {
  const bStart = toMinutes(booking.time);
  const bEnd = bStart + Number(booking.duration);
  return !(endMin <= bStart || startMin >= bEnd);
}

function isSlotBusy(time) {
  if (!state.selectedTeacher || !state.selectedDate) return true;
  const startMin = toMinutes(time);
  const endMin = startMin + SLOT_STEP;
  return state.bookings.some(b =>
    b.teacher === state.selectedTeacher &&
    b.date === state.selectedDate &&
    bookingOverlaps(b, startMin, endMin)
  );
}

function isSelectionConflicting(time) {
  if (!state.selectedTeacher || !state.selectedDate) return true;
  const startMin = toMinutes(time);
  const endMin = startMin + Number(state.duration);
  return state.bookings.some(b =>
    b.teacher === state.selectedTeacher &&
    b.date === state.selectedDate &&
    bookingOverlaps(b, startMin, endMin)
  );
}

function renderTeachers() {
  teachersEl.innerHTML = "";
  state.teachers.forEach(name => {
    const el = document.createElement("div");
    el.className = "teacher" + (state.selectedTeacher === name ? " active" : "");
    el.textContent = name;
    el.addEventListener("click", () => {
      state.selectedTeacher = name;
      state.selectedTime = null;
      renderTeachers();
      renderSlots();
      updateStatus();
    });
    teachersEl.appendChild(el);
  });
}

function renderSlots() {
  const slots = buildSlots();
  slotsEl.innerHTML = "";
  slots.forEach(time => {
    const el = document.createElement("button");
    const busy = isSlotBusy(time);
    el.className = "slot" + (busy ? " busy" : "") + (state.selectedTime === time ? " selected" : "");
    el.textContent = time;
    el.disabled = busy;
    el.addEventListener("click", () => {
      if (busy) return;
      state.selectedTime = time;
      renderSlots();
      updateStatus();
    });
    slotsEl.appendChild(el);
  });
}

function updateStatus() {
  if (!state.selectedTeacher) {
    statusText.textContent = "Оберіть вчителя";
    bookBtn.disabled = true;
    return;
  }
  if (!state.selectedTime) {
    statusText.textContent = `Вчитель: ${state.selectedTeacher}. Оберіть час`;
    bookBtn.disabled = true;
    return;
  }
  if (isSelectionConflicting(state.selectedTime)) {
    statusText.textContent = "Обраний час зайнятий";
    bookBtn.disabled = true;
    return;
  }
  statusText.textContent = `Вчитель: ${state.selectedTeacher}. ${state.selectedDate} о ${state.selectedTime}`;
  bookBtn.disabled = false;
}

async function loadTeachers() {
  const res = await fetch("api/teachers");
  const data = await res.json();
  state.teachers = data.teachers || [];
  renderTeachers();
}

async function loadBookings() {
  const res = await fetch("api/bookings");
  const data = await res.json();
  state.bookings = data.bookings || [];
  renderSlots();
  updateStatus();
}

async function bookLesson() {
  resultEl.textContent = "";
  const payload = {
    teacher: state.selectedTeacher,
    date: state.selectedDate,
    time: state.selectedTime,
    duration: Number(state.duration),
  };
  const res = await fetch("api/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    resultEl.textContent = data.error || "Помилка бронювання";
    return;
  }
  resultEl.textContent = "Урок заброньовано. Час позначено як зайнятий.";
  await loadBookings();
}

function init() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  state.selectedDate = `${yyyy}-${mm}-${dd}`;
  dateInput.value = state.selectedDate;

  dateInput.addEventListener("change", (e) => {
    state.selectedDate = e.target.value;
    state.selectedTime = null;
    renderSlots();
    updateStatus();
  });

  durationSelect.addEventListener("change", (e) => {
    state.duration = Number(e.target.value);
    updateStatus();
  });

  bookBtn.addEventListener("click", bookLesson);

  loadTeachers();
  loadBookings();
  setInterval(loadBookings, 15000);
}

init();
