const state = {
  teachers: [],
  bookings: [],
  selectedTeacher: null,
  selectedDate: null,
};

const teacherSelect = document.getElementById("teacherSelect");
const dateInput = document.getElementById("dateInput");
const statusText = document.getElementById("statusText");
const daySchedule = document.getElementById("daySchedule");
const allBookings = document.getElementById("allBookings");

const SLOT_STEP = 30;
const START_HOUR = 8;
const END_HOUR = 20;

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

function renderTeacherOptions() {
  teacherSelect.innerHTML = "";
  state.teachers.forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    teacherSelect.appendChild(opt);
  });
  state.selectedTeacher = state.teachers[0] || null;
  teacherSelect.value = state.selectedTeacher || "";
}

function renderSchedule() {
  daySchedule.innerHTML = "";
  if (!state.selectedTeacher || !state.selectedDate) return;

  const dayBookings = state.bookings.filter(b =>
    b.teacher === state.selectedTeacher && b.date === state.selectedDate
  );

  const slots = buildSlots();
  slots.forEach(time => {
    const row = document.createElement("div");
    const busy = dayBookings.some(b => {
      const start = time;
      const end = minutesToTime(
        parseInt(time.split(":")[0]) * 60 +
        parseInt(time.split(":")[1]) + SLOT_STEP
      );
      const bStart = b.time;
      const bEnd = minutesToTime(
        parseInt(b.time.split(":")[0]) * 60 +
        parseInt(b.time.split(":")[1]) + Number(b.duration)
      );
      return !(end <= bStart || start >= bEnd);
    });

    row.className = "schedule-row" + (busy ? " busy" : "");
    row.innerHTML = `
      <strong>${time}</strong>
      <div>${busy ? "Зайнято" : "Вільно"}</div>
    `;
    daySchedule.appendChild(row);
  });
}

function renderAllBookings() {
  allBookings.innerHTML = "";
  if (!state.bookings.length) {
    allBookings.textContent = "Немає бронювань";
    return;
  }
  state.bookings
    .slice()
    .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time))
    .forEach(b => {
      const card = document.createElement("div");
      card.className = "booking-card";
      card.innerHTML = `
        <strong>${b.teacher}</strong>
        ${b.date} о ${b.time} (тривалість ${b.duration} хв)
      `;
      allBookings.appendChild(card);
    });
}

function updateStatus() {
  if (!state.selectedTeacher) {
    statusText.textContent = "Оберіть вчителя";
    return;
  }
  statusText.textContent = `Вчитель: ${state.selectedTeacher}. Дата: ${state.selectedDate}`;
}

async function loadTeachers() {
  const res = await fetch("api/teachers");
  const data = await res.json();
  state.teachers = data.teachers || [];
  renderTeacherOptions();
}

async function loadBookings() {
  const res = await fetch("api/bookings");
  const data = await res.json();
  state.bookings = data.bookings || [];
  renderSchedule();
  renderAllBookings();
  updateStatus();
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
    renderSchedule();
    updateStatus();
  });

  teacherSelect.addEventListener("change", (e) => {
    state.selectedTeacher = e.target.value;
    renderSchedule();
    updateStatus();
  });

  loadTeachers();
  loadBookings();
  setInterval(loadBookings, 15000);
}

init();
