// Teacher CRM frontend: plain JS, talks to the FastAPI backend on the same origin.

const state = { token: localStorage.getItem("token"), students: [], subjects: [], subjectId: null };
const $ = (id) => document.getElementById(id);

// Build DOM nodes; text always goes through text nodes, never innerHTML
function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else if (key === "class") el.className = value;
    else el.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child !== null && child !== undefined) el.append(child instanceof Node ? child : String(child));
  }
  return el;
}

async function api(method, path, body) {
  const headers = { "Content-Type": "application/json" };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { method, headers, body: body && JSON.stringify(body) });
  if (response.status === 401 && state.token) {
    logout();
    throw new Error("Session expired, please log in again");
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => d.msg).join("; ") : data.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

// Run an action and show its error instead of failing silently
async function run(action, errorId = "app-error") {
  $(errorId).textContent = "";
  try {
    await action();
  } catch (error) {
    $(errorId).textContent = error.message;
  }
}

const formData = (form) => Object.fromEntries(new FormData(form).entries());
const emptyToNull = (obj) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, v === "" ? null : v]));
const fmt = (x) => (Math.round(x * 100) / 100).toString();

// ---------- auth ----------
$("auth-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const action = event.submitter.dataset.action;
  const { email, password } = formData(event.target);
  run(async () => {
    if (action === "register") await api("POST", "/auth/register", { email, password });
    const { access_token } = await api("POST", "/auth/login", { email, password });
    state.token = access_token;
    localStorage.setItem("token", access_token);
    await start();
  }, "auth-error");
});

$("logout").addEventListener("click", async () => {
  await api("POST", "/auth/logout").catch(() => {});
  logout();
});

function logout() {
  state.token = null;
  localStorage.removeItem("token");
  $("app-view").hidden = true;
  $("auth-view").hidden = false;
}

// ---------- tabs ----------
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => showTab(tab.dataset.tab)));

function showTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((p) => (p.hidden = p.id !== `tab-${name}`));
  if (name === "plans") renderPlans();
}

// ---------- students ----------
async function loadStudents() {
  state.students = await api("GET", "/students");
  $("students-body").replaceChildren(
    ...state.students.map((s) =>
      h("tr", {},
        h("td", {}, s.full_name), h("td", {}, s.class_name),
        h("td", {}, s.parent_phone ?? ""), h("td", {}, s.notes ?? ""),
        h("td", {}, h("button", { class: "danger", onclick: () => deleteStudent(s) }, "Delete")),
      ),
    ),
  );
}

$("student-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    await api("POST", "/students", emptyToNull(formData(event.target)));
    event.target.reset();
    await loadStudents();
  });
});

function deleteStudent(student) {
  if (!confirm(`Delete ${student.full_name} and all their scores?`)) return;
  run(async () => {
    await api("DELETE", `/students/${student.id}`);
    await loadStudents();
    await renderSubject();
  });
}

// ---------- subjects ----------
async function loadSubjects() {
  state.subjects = await api("GET", "/subjects");
  if (!state.subjects.some((s) => s.id === state.subjectId)) state.subjectId = state.subjects[0]?.id ?? null;
  $("subject-list").replaceChildren(
    ...state.subjects.map((s) =>
      h("li", { class: s.id === state.subjectId ? "active" : "", onclick: () => selectSubject(s.id) },
        `${s.name} (grade ${s.grade})`),
    ),
  );
  $("plan-subject").replaceChildren(
    ...state.subjects.map((s) => h("option", { value: s.id }, `${s.name} (grade ${s.grade})`)),
  );
  await renderSubject();
}

async function selectSubject(id) {
  state.subjectId = id;
  await run(loadSubjects);
}

$("subject-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const { name, grade } = formData(event.target);
  run(async () => {
    const subject = await api("POST", "/subjects", { name, grade: Number(grade) });
    event.target.reset();
    state.subjectId = subject.id;
    await loadSubjects();
  });
});

async function renderSubject() {
  const detail = $("subject-detail");
  const subject = state.subjects.find((s) => s.id === state.subjectId);
  if (!subject) {
    detail.replaceChildren(h("div", { class: "card muted" }, "Add a subject to start."));
    return;
  }
  const scores = await api("GET", `/subjects/${subject.id}/scores`);
  const stats = scores.length >= 2 ? await api("GET", `/subjects/${subject.id}/stats`) : null;

  const scoreForm = h("form", { class: "inline-form", onsubmit: (event) => addScore(event, subject.id) },
    h("select", { name: "student_id", required: "" },
      ...state.students.map((s) => h("option", { value: s.id }, `${s.full_name} (${s.class_name})`))),
    h("input", { name: "value", type: "number", min: "0", max: "100", step: "0.1", placeholder: "Score, %", required: "" }),
    h("button", { type: "submit" }, "Add score"),
  );

  detail.replaceChildren(
    h("div", { class: "card row" },
      h("h2", {}, `${subject.name}, grade ${subject.grade}`),
      h("span", { class: "spacer" }),
      h("button", { class: "danger", onclick: () => deleteSubject(subject) }, "Delete subject"),
    ),
    stats ? statsCard(stats) : h("div", { class: "card muted" }, "Statistics appear after at least two scores."),
    h("div", { class: "card stack" },
      h("h2", {}, "Scores"),
      scoreForm,
      h("table", {},
        h("thead", {}, h("tr", {}, h("th", {}, "Student"), h("th", {}, "Score, %"), h("th", {}, "Mark"), h("th", {}))),
        h("tbody", {},
          ...scores.map((s) =>
            h("tr", {},
              h("td", {}, s.student_name), h("td", {}, fmt(s.value)),
              h("td", {}, h("span", { class: "mark" }, s.mark)),
              h("td", {}, h("button", { class: "danger", onclick: () => deleteScore(subject.id, s.id) }, "Delete")),
            ),
          ),
        ),
      ),
    ),
  );
}

function statsCard({ summary, marks, pass_rate }) {
  const stat = (label, value) => h("div", { class: "stat" }, h("div", { class: "muted small" }, label), h("div", { class: "value" }, value));
  const max = Math.max(...Object.values(marks), 1);
  return h("div", { class: "card stack" },
    h("div", { class: "stats" },
      stat("Students", summary.count), stat("Mean, %", fmt(summary.mean)), stat("Median, %", fmt(summary.median)),
      stat("Std. deviation", fmt(summary.stdev)), stat("Pass rate", `${Math.round(pass_rate * 100)}%`),
    ),
    h("div", { class: "bars" },
      ...["5", "4", "3", "2"].map((mark) =>
        h("div", { class: "bar" },
          h("span", {}, `Mark ${mark}`),
          h("div", {}, h("div", { class: "fill", style: `width: ${(marks[mark] / max) * 100}%` })),
          h("span", {}, marks[mark]),
        ),
      ),
    ),
  );
}

function addScore(event, subjectId) {
  event.preventDefault();
  const { student_id, value } = formData(event.target);
  run(async () => {
    await api("POST", `/subjects/${subjectId}/scores`, { student_id: Number(student_id), value: Number(value) });
    await renderSubject();
  });
}

function deleteScore(subjectId, scoreId) {
  run(async () => {
    await api("DELETE", `/subjects/${subjectId}/scores/${scoreId}`);
    await renderSubject();
  });
}

function deleteSubject(subject) {
  if (!confirm(`Delete ${subject.name} with all scores and plans?`)) return;
  run(async () => {
    await api("DELETE", `/subjects/${subject.id}`);
    await loadSubjects();
  });
}

// ---------- lesson plans (KSP) ----------
async function renderPlans() {
  const subjectId = $("plan-subject").value;
  if (!subjectId) {
    $("plan-list").replaceChildren();
    return;
  }
  const plans = await api("GET", `/subjects/${subjectId}/plans`);
  $("plan-list").replaceChildren(
    ...plans.map((p) =>
      h("li", { onclick: () => ($("plan-content").textContent = p.content) },
        h("div", {}, p.topic),
        h("div", { class: "row small muted" },
          new Date(p.created_at).toLocaleString(), h("span", { class: "badge" }, p.source),
          h("span", { class: "spacer" }),
          h("button", { class: "danger", onclick: (e) => { e.stopPropagation(); deletePlan(subjectId, p.id); } }, "Delete"),
        ),
      ),
    ),
  );
}

$("plan-subject").addEventListener("change", () => run(renderPlans));

$("plan-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const { subject_id, topic, objectives } = formData(event.target);
  const button = event.target.querySelector("button");
  button.disabled = true;
  button.textContent = "Generating...";
  run(async () => {
    try {
      const plan = await api("POST", `/subjects/${subject_id}/plans`, { topic, objectives: objectives || null });
      $("plan-content").textContent = plan.content;
      event.target.topic.value = "";
      event.target.objectives.value = "";
      await renderPlans();
    } finally {
      button.disabled = false;
      button.textContent = "Generate";
    }
  });
});

function deletePlan(subjectId, planId) {
  run(async () => {
    await api("DELETE", `/subjects/${subjectId}/plans/${planId}`);
    $("plan-content").textContent = "Select or generate a plan.";
    await renderPlans();
  });
}

// ---------- start ----------
async function start() {
  const me = await api("GET", "/auth/me");
  $("user-email").textContent = me.email;
  $("auth-view").hidden = true;
  $("app-view").hidden = false;
  await loadStudents();
  await loadSubjects();
  showTab("students");
}

if (state.token) start().catch(logout);
else logout();
